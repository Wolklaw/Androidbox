import queue
import threading
import time

import grpc
from google.protobuf import empty_pb2

from .proto import emulator_controller_pb2 as pb
from .proto import emulator_controller_pb2_grpc as rpc

KEYDOWN = pb.KeyboardEvent.keydown
KEYUP = pb.KeyboardEvent.keyup
KEYPRESS = pb.KeyboardEvent.keypress


class Bridge:
    def __init__(self, port, token):
        self.channel = grpc.insecure_channel(f"127.0.0.1:{port}",
                                             options=[("grpc.max_receive_message_length", 256 << 20)])
        self.stub = rpc.EmulatorControllerStub(self.channel)
        self.metadata = [("authorization", f"Bearer {token}")]
        self.outbox = queue.Queue()
        self.screen = None
        self.recording = None
        self.mirrors = []
        self.closed = False
        threading.Thread(target=self.deliver, daemon=True).start()

    def deliver(self):
        while not self.closed:
            try:
                self.stub.streamInputEvent(iter(self.outbox.get, None), metadata=self.metadata)
            except grpc.RpcError:
                time.sleep(0.5)

    def request(self, method, message=None, timeout=10):
        return getattr(self.stub, method)(message or empty_pb2.Empty(), metadata=self.metadata, timeout=timeout)

    def send(self, event, record=True):
        self.outbox.put(event)
        if record and self.recording is not None:
            self.recording.append((time.monotonic(), event.SerializeToString()))
        for mirror in self.mirrors:
            mirror.outbox.put(event)

    def replay(self, payload):
        event = pb.InputEvent()
        event.ParseFromString(payload)
        self.send(event, record=False)

    def touch(self, *touches):
        points = [pb.Touch(x=round(x), y=round(y), identifier=identifier, pressure=1 if down else 0)
                  for identifier, x, y, down in touches]
        self.send(pb.InputEvent(touch_event=pb.TouchEvent(touches=points)))

    def key(self, key, kind=KEYPRESS):
        self.send(pb.InputEvent(key_event=pb.KeyboardEvent(key=key, eventType=kind)))

    def type(self, text):
        self.send(pb.InputEvent(key_event=pb.KeyboardEvent(text=text)))

    def watch(self, width, height, on_frame):
        self.unwatch()
        request = pb.ImageFormat(format=pb.ImageFormat.RGB888, width=width, height=height)
        self.screen = call = self.stub.streamScreenshot(request, metadata=self.metadata)

        def pump():
            try:
                for image in call:
                    on_frame(image.image, image.format.width, image.format.height, image.format.rotation.rotation)
            except grpc.RpcError:
                pass

        threading.Thread(target=pump, daemon=True).start()

    def unwatch(self):
        if self.screen:
            self.screen.cancel()
            self.screen = None

    def rotate(self, degrees):
        self.request("setPhysicalModel", pb.PhysicalModelValue(
            target=pb.PhysicalModelValue.ROTATION, value=pb.ParameterValue(data=[0, 0, degrees])))

    def rotation(self):
        model = self.request("getPhysicalModel", pb.PhysicalModelValue(target=pb.PhysicalModelValue.ROTATION))
        return round(model.value.data[2]) if len(model.value.data) > 2 else 0

    def shake(self):
        for amplitude in (3.0, 0.0):
            self.request("setPhysicalModel", pb.PhysicalModelValue(
                target=pb.PhysicalModelValue.AMBIENT_MOTION, value=pb.ParameterValue(data=[amplitude])))
            time.sleep(1.2)

    def locate(self, latitude, longitude):
        self.request("setGps", pb.GpsState(passiveUpdate=True, latitude=latitude, longitude=longitude,
                                           altitude=10, satellites=12))

    def screenshot(self):
        return self.request("getScreenshot", pb.ImageFormat(format=pb.ImageFormat.PNG), timeout=20).image

    def set_clipboard(self, text):
        self.request("setClipboard", pb.ClipData(text=text))

    def watch_clipboard(self, on_text):
        def pump():
            try:
                for clip in self.stub.streamClipboard(empty_pb2.Empty(), metadata=self.metadata):
                    on_text(clip.text)
            except grpc.RpcError:
                pass

        threading.Thread(target=pump, daemon=True).start()

    def close(self):
        self.closed = True
        self.unwatch()
        self.outbox.put(None)
        self.channel.close()
