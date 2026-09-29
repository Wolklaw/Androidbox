import grpc
import warnings
from androidbox.proto import emulator_controller_pb2 as androidbox_dot_proto_dot_emulator__controller__pb2
from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
GRPC_GENERATED_VERSION = '1.84.0'
GRPC_VERSION = grpc.__version__
_version_not_supported = False
try:
    from grpc._utilities import first_version_is_lower
    _version_not_supported = first_version_is_lower(GRPC_VERSION, GRPC_GENERATED_VERSION)
except ImportError:
    _version_not_supported = True
if _version_not_supported:
    raise RuntimeError(f'The grpc package installed is at version {GRPC_VERSION},' + ' but the generated code in androidbox/proto/emulator_controller_pb2_grpc.py depends on' + f' grpcio>={GRPC_GENERATED_VERSION}.' + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}' + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.')

class EmulatorControllerStub:

    def __init__(self, channel):
        self.streamSensor = channel.unary_stream('/android.emulation.control.EmulatorController/streamSensor', request_serializer=androidbox_dot_proto_dot_emulator__controller__pb2.SensorValue.SerializeToString, response_deserializer=androidbox_dot_proto_dot_emulator__controller__pb2.SensorValue.FromString, _registered_method=True)
        self.getSensor = channel.unary_unary('/android.emulation.control.EmulatorController/getSensor', request_serializer=androidbox_dot_proto_dot_emulator__controller__pb2.SensorValue.SerializeToString, response_deserializer=androidbox_dot_proto_dot_emulator__controller__pb2.SensorValue.FromString, _registered_method=True)
        self.setSensor = channel.unary_unary('/android.emulation.control.EmulatorController/setSensor', request_serializer=androidbox_dot_proto_dot_emulator__controller__pb2.SensorValue.SerializeToString, response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString, _registered_method=True)
        self.setPhysicalModel = channel.unary_unary('/android.emulation.control.EmulatorController/setPhysicalModel', request_serializer=androidbox_dot_proto_dot_emulator__controller__pb2.PhysicalModelValue.SerializeToString, response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString, _registered_method=True)
        self.getPhysicalModel = channel.unary_unary('/android.emulation.control.EmulatorController/getPhysicalModel', request_serializer=androidbox_dot_proto_dot_emulator__controller__pb2.PhysicalModelValue.SerializeToString, response_deserializer=androidbox_dot_proto_dot_emulator__controller__pb2.PhysicalModelValue.FromString, _registered_method=True)
        self.streamPhysicalModel = channel.unary_stream('/android.emulation.control.EmulatorController/streamPhysicalModel', request_serializer=androidbox_dot_proto_dot_emulator__controller__pb2.PhysicalModelValue.SerializeToString, response_deserializer=androidbox_dot_proto_dot_emulator__controller__pb2.PhysicalModelValue.FromString, _registered_method=True)
        self.setClipboard = channel.unary_unary('/android.emulation.control.EmulatorController/setClipboard', request_serializer=androidbox_dot_proto_dot_emulator__controller__pb2.ClipData.SerializeToString, response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString, _registered_method=True)
        self.getClipboard = channel.unary_unary('/android.emulation.control.EmulatorController/getClipboard', request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, response_deserializer=androidbox_dot_proto_dot_emulator__controller__pb2.ClipData.FromString, _registered_method=True)
        self.streamClipboard = channel.unary_stream('/android.emulation.control.EmulatorController/streamClipboard', request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, response_deserializer=androidbox_dot_proto_dot_emulator__controller__pb2.ClipData.FromString, _registered_method=True)
        self.setBattery = channel.unary_unary('/android.emulation.control.EmulatorController/setBattery', request_serializer=androidbox_dot_proto_dot_emulator__controller__pb2.BatteryState.SerializeToString, response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString, _registered_method=True)
        self.getBattery = channel.unary_unary('/android.emulation.control.EmulatorController/getBattery', request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, response_deserializer=androidbox_dot_proto_dot_emulator__controller__pb2.BatteryState.FromString, _registered_method=True)
        self.setGps = channel.unary_unary('/android.emulation.control.EmulatorController/setGps', request_serializer=androidbox_dot_proto_dot_emulator__controller__pb2.GpsState.SerializeToString, response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString, _registered_method=True)
        self.getGps = channel.unary_unary('/android.emulation.control.EmulatorController/getGps', request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, response_deserializer=androidbox_dot_proto_dot_emulator__controller__pb2.GpsState.FromString, _registered_method=True)
        self.sendFingerprint = channel.unary_unary('/android.emulation.control.EmulatorController/sendFingerprint', request_serializer=androidbox_dot_proto_dot_emulator__controller__pb2.Fingerprint.SerializeToString, response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString, _registered_method=True)
        self.sendKey = channel.unary_unary('/android.emulation.control.EmulatorController/sendKey', request_serializer=androidbox_dot_proto_dot_emulator__controller__pb2.KeyboardEvent.SerializeToString, response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString, _registered_method=True)
        self.sendTouch = channel.unary_unary('/android.emulation.control.EmulatorController/sendTouch', request_serializer=androidbox_dot_proto_dot_emulator__controller__pb2.TouchEvent.SerializeToString, response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString, _registered_method=True)
        self.sendMouse = channel.unary_unary('/android.emulation.control.EmulatorController/sendMouse', request_serializer=androidbox_dot_proto_dot_emulator__controller__pb2.MouseEvent.SerializeToString, response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString, _registered_method=True)
        self.injectWheel = channel.stream_unary('/android.emulation.control.EmulatorController/injectWheel', request_serializer=androidbox_dot_proto_dot_emulator__controller__pb2.WheelEvent.SerializeToString, response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString, _registered_method=True)
        self.streamInputEvent = channel.stream_unary('/android.emulation.control.EmulatorController/streamInputEvent', request_serializer=androidbox_dot_proto_dot_emulator__controller__pb2.InputEvent.SerializeToString, response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString, _registered_method=True)
        self.sendPhone = channel.unary_unary('/android.emulation.control.EmulatorController/sendPhone', request_serializer=androidbox_dot_proto_dot_emulator__controller__pb2.PhoneCall.SerializeToString, response_deserializer=androidbox_dot_proto_dot_emulator__controller__pb2.PhoneResponse.FromString, _registered_method=True)
        self.sendSms = channel.unary_unary('/android.emulation.control.EmulatorController/sendSms', request_serializer=androidbox_dot_proto_dot_emulator__controller__pb2.SmsMessage.SerializeToString, response_deserializer=androidbox_dot_proto_dot_emulator__controller__pb2.PhoneResponse.FromString, _registered_method=True)
        self.setPhoneNumber = channel.unary_unary('/android.emulation.control.EmulatorController/setPhoneNumber', request_serializer=androidbox_dot_proto_dot_emulator__controller__pb2.PhoneNumber.SerializeToString, response_deserializer=androidbox_dot_proto_dot_emulator__controller__pb2.PhoneResponse.FromString, _registered_method=True)
        self.getStatus = channel.unary_unary('/android.emulation.control.EmulatorController/getStatus', request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, response_deserializer=androidbox_dot_proto_dot_emulator__controller__pb2.EmulatorStatus.FromString, _registered_method=True)
        self.getScreenshot = channel.unary_unary('/android.emulation.control.EmulatorController/getScreenshot', request_serializer=androidbox_dot_proto_dot_emulator__controller__pb2.ImageFormat.SerializeToString, response_deserializer=androidbox_dot_proto_dot_emulator__controller__pb2.Image.FromString, _registered_method=True)
        self.streamScreenshot = channel.unary_stream('/android.emulation.control.EmulatorController/streamScreenshot', request_serializer=androidbox_dot_proto_dot_emulator__controller__pb2.ImageFormat.SerializeToString, response_deserializer=androidbox_dot_proto_dot_emulator__controller__pb2.Image.FromString, _registered_method=True)
        self.streamAudio = channel.unary_stream('/android.emulation.control.EmulatorController/streamAudio', request_serializer=androidbox_dot_proto_dot_emulator__controller__pb2.AudioFormat.SerializeToString, response_deserializer=androidbox_dot_proto_dot_emulator__controller__pb2.AudioPacket.FromString, _registered_method=True)
        self.injectAudio = channel.stream_unary('/android.emulation.control.EmulatorController/injectAudio', request_serializer=androidbox_dot_proto_dot_emulator__controller__pb2.AudioPacket.SerializeToString, response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString, _registered_method=True)
        self.getMicrophoneState = channel.unary_unary('/android.emulation.control.EmulatorController/getMicrophoneState', request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, response_deserializer=androidbox_dot_proto_dot_emulator__controller__pb2.MicrophoneState.FromString, _registered_method=True)
        self.setMicrophoneState = channel.unary_unary('/android.emulation.control.EmulatorController/setMicrophoneState', request_serializer=androidbox_dot_proto_dot_emulator__controller__pb2.MicrophoneState.SerializeToString, response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString, _registered_method=True)
        self.getLogcat = channel.unary_unary('/android.emulation.control.EmulatorController/getLogcat', request_serializer=androidbox_dot_proto_dot_emulator__controller__pb2.LogMessage.SerializeToString, response_deserializer=androidbox_dot_proto_dot_emulator__controller__pb2.LogMessage.FromString, _registered_method=True)
        self.streamLogcat = channel.unary_stream('/android.emulation.control.EmulatorController/streamLogcat', request_serializer=androidbox_dot_proto_dot_emulator__controller__pb2.LogMessage.SerializeToString, response_deserializer=androidbox_dot_proto_dot_emulator__controller__pb2.LogMessage.FromString, _registered_method=True)
        self.setVmState = channel.unary_unary('/android.emulation.control.EmulatorController/setVmState', request_serializer=androidbox_dot_proto_dot_emulator__controller__pb2.VmRunState.SerializeToString, response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString, _registered_method=True)
        self.getVmState = channel.unary_unary('/android.emulation.control.EmulatorController/getVmState', request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, response_deserializer=androidbox_dot_proto_dot_emulator__controller__pb2.VmRunState.FromString, _registered_method=True)
        self.setDisplayConfigurations = channel.unary_unary('/android.emulation.control.EmulatorController/setDisplayConfigurations', request_serializer=androidbox_dot_proto_dot_emulator__controller__pb2.DisplayConfigurations.SerializeToString, response_deserializer=androidbox_dot_proto_dot_emulator__controller__pb2.DisplayConfigurations.FromString, _registered_method=True)
        self.getDisplayConfigurations = channel.unary_unary('/android.emulation.control.EmulatorController/getDisplayConfigurations', request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, response_deserializer=androidbox_dot_proto_dot_emulator__controller__pb2.DisplayConfigurations.FromString, _registered_method=True)
        self.streamNotification = channel.unary_stream('/android.emulation.control.EmulatorController/streamNotification', request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, response_deserializer=androidbox_dot_proto_dot_emulator__controller__pb2.Notification.FromString, _registered_method=True)
        self.rotateVirtualSceneCamera = channel.unary_unary('/android.emulation.control.EmulatorController/rotateVirtualSceneCamera', request_serializer=androidbox_dot_proto_dot_emulator__controller__pb2.RotationRadian.SerializeToString, response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString, _registered_method=True)
        self.setVirtualSceneCameraVelocity = channel.unary_unary('/android.emulation.control.EmulatorController/setVirtualSceneCameraVelocity', request_serializer=androidbox_dot_proto_dot_emulator__controller__pb2.Velocity.SerializeToString, response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString, _registered_method=True)
        self.setPosture = channel.unary_unary('/android.emulation.control.EmulatorController/setPosture', request_serializer=androidbox_dot_proto_dot_emulator__controller__pb2.Posture.SerializeToString, response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString, _registered_method=True)
        self.getBrightness = channel.unary_unary('/android.emulation.control.EmulatorController/getBrightness', request_serializer=androidbox_dot_proto_dot_emulator__controller__pb2.BrightnessValue.SerializeToString, response_deserializer=androidbox_dot_proto_dot_emulator__controller__pb2.BrightnessValue.FromString, _registered_method=True)
        self.setBrightness = channel.unary_unary('/android.emulation.control.EmulatorController/setBrightness', request_serializer=androidbox_dot_proto_dot_emulator__controller__pb2.BrightnessValue.SerializeToString, response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString, _registered_method=True)
        self.getDisplayMode = channel.unary_unary('/android.emulation.control.EmulatorController/getDisplayMode', request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, response_deserializer=androidbox_dot_proto_dot_emulator__controller__pb2.DisplayMode.FromString, _registered_method=True)
        self.setDisplayMode = channel.unary_unary('/android.emulation.control.EmulatorController/setDisplayMode', request_serializer=androidbox_dot_proto_dot_emulator__controller__pb2.DisplayMode.SerializeToString, response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString, _registered_method=True)
        self.setXrOptions = channel.unary_unary('/android.emulation.control.EmulatorController/setXrOptions', request_serializer=androidbox_dot_proto_dot_emulator__controller__pb2.XrOptions.SerializeToString, response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString, _registered_method=True)
        self.getXrOptions = channel.unary_unary('/android.emulation.control.EmulatorController/getXrOptions', request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, response_deserializer=androidbox_dot_proto_dot_emulator__controller__pb2.XrOptions.FromString, _registered_method=True)
        self.setEnvironment = channel.unary_unary('/android.emulation.control.EmulatorController/setEnvironment', request_serializer=androidbox_dot_proto_dot_emulator__controller__pb2.Environment.SerializeToString, response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString, _registered_method=True)
        self.getEnvironment = channel.unary_unary('/android.emulation.control.EmulatorController/getEnvironment', request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, response_deserializer=androidbox_dot_proto_dot_emulator__controller__pb2.Environment.FromString, _registered_method=True)
        self.getHostCameras = channel.unary_unary('/android.emulation.control.EmulatorController/getHostCameras', request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, response_deserializer=androidbox_dot_proto_dot_emulator__controller__pb2.CameraList.FromString, _registered_method=True)

class EmulatorControllerServicer:

    def streamSensor(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def getSensor(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def setSensor(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def setPhysicalModel(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def getPhysicalModel(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def streamPhysicalModel(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def setClipboard(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def getClipboard(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def streamClipboard(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def setBattery(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def getBattery(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def setGps(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def getGps(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def sendFingerprint(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def sendKey(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def sendTouch(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def sendMouse(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def injectWheel(self, request_iterator, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def streamInputEvent(self, request_iterator, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def sendPhone(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def sendSms(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def setPhoneNumber(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def getStatus(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def getScreenshot(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def streamScreenshot(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def streamAudio(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def injectAudio(self, request_iterator, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def getMicrophoneState(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def setMicrophoneState(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def getLogcat(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def streamLogcat(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def setVmState(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def getVmState(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def setDisplayConfigurations(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def getDisplayConfigurations(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def streamNotification(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def rotateVirtualSceneCamera(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def setVirtualSceneCameraVelocity(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def setPosture(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def getBrightness(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def setBrightness(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def getDisplayMode(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def setDisplayMode(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def setXrOptions(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def getXrOptions(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def setEnvironment(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def getEnvironment(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def getHostCameras(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

def add_EmulatorControllerServicer_to_server(servicer, server):
    rpc_method_handlers = {'streamSensor': grpc.unary_stream_rpc_method_handler(servicer.streamSensor, request_deserializer=androidbox_dot_proto_dot_emulator__controller__pb2.SensorValue.FromString, response_serializer=androidbox_dot_proto_dot_emulator__controller__pb2.SensorValue.SerializeToString), 'getSensor': grpc.unary_unary_rpc_method_handler(servicer.getSensor, request_deserializer=androidbox_dot_proto_dot_emulator__controller__pb2.SensorValue.FromString, response_serializer=androidbox_dot_proto_dot_emulator__controller__pb2.SensorValue.SerializeToString), 'setSensor': grpc.unary_unary_rpc_method_handler(servicer.setSensor, request_deserializer=androidbox_dot_proto_dot_emulator__controller__pb2.SensorValue.FromString, response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString), 'setPhysicalModel': grpc.unary_unary_rpc_method_handler(servicer.setPhysicalModel, request_deserializer=androidbox_dot_proto_dot_emulator__controller__pb2.PhysicalModelValue.FromString, response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString), 'getPhysicalModel': grpc.unary_unary_rpc_method_handler(servicer.getPhysicalModel, request_deserializer=androidbox_dot_proto_dot_emulator__controller__pb2.PhysicalModelValue.FromString, response_serializer=androidbox_dot_proto_dot_emulator__controller__pb2.PhysicalModelValue.SerializeToString), 'streamPhysicalModel': grpc.unary_stream_rpc_method_handler(servicer.streamPhysicalModel, request_deserializer=androidbox_dot_proto_dot_emulator__controller__pb2.PhysicalModelValue.FromString, response_serializer=androidbox_dot_proto_dot_emulator__controller__pb2.PhysicalModelValue.SerializeToString), 'setClipboard': grpc.unary_unary_rpc_method_handler(servicer.setClipboard, request_deserializer=androidbox_dot_proto_dot_emulator__controller__pb2.ClipData.FromString, response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString), 'getClipboard': grpc.unary_unary_rpc_method_handler(servicer.getClipboard, request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString, response_serializer=androidbox_dot_proto_dot_emulator__controller__pb2.ClipData.SerializeToString), 'streamClipboard': grpc.unary_stream_rpc_method_handler(servicer.streamClipboard, request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString, response_serializer=androidbox_dot_proto_dot_emulator__controller__pb2.ClipData.SerializeToString), 'setBattery': grpc.unary_unary_rpc_method_handler(servicer.setBattery, request_deserializer=androidbox_dot_proto_dot_emulator__controller__pb2.BatteryState.FromString, response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString), 'getBattery': grpc.unary_unary_rpc_method_handler(servicer.getBattery, request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString, response_serializer=androidbox_dot_proto_dot_emulator__controller__pb2.BatteryState.SerializeToString), 'setGps': grpc.unary_unary_rpc_method_handler(servicer.setGps, request_deserializer=androidbox_dot_proto_dot_emulator__controller__pb2.GpsState.FromString, response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString), 'getGps': grpc.unary_unary_rpc_method_handler(servicer.getGps, request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString, response_serializer=androidbox_dot_proto_dot_emulator__controller__pb2.GpsState.SerializeToString), 'sendFingerprint': grpc.unary_unary_rpc_method_handler(servicer.sendFingerprint, request_deserializer=androidbox_dot_proto_dot_emulator__controller__pb2.Fingerprint.FromString, response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString), 'sendKey': grpc.unary_unary_rpc_method_handler(servicer.sendKey, request_deserializer=androidbox_dot_proto_dot_emulator__controller__pb2.KeyboardEvent.FromString, response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString), 'sendTouch': grpc.unary_unary_rpc_method_handler(servicer.sendTouch, request_deserializer=androidbox_dot_proto_dot_emulator__controller__pb2.TouchEvent.FromString, response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString), 'sendMouse': grpc.unary_unary_rpc_method_handler(servicer.sendMouse, request_deserializer=androidbox_dot_proto_dot_emulator__controller__pb2.MouseEvent.FromString, response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString), 'injectWheel': grpc.stream_unary_rpc_method_handler(servicer.injectWheel, request_deserializer=androidbox_dot_proto_dot_emulator__controller__pb2.WheelEvent.FromString, response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString), 'streamInputEvent': grpc.stream_unary_rpc_method_handler(servicer.streamInputEvent, request_deserializer=androidbox_dot_proto_dot_emulator__controller__pb2.InputEvent.FromString, response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString), 'sendPhone': grpc.unary_unary_rpc_method_handler(servicer.sendPhone, request_deserializer=androidbox_dot_proto_dot_emulator__controller__pb2.PhoneCall.FromString, response_serializer=androidbox_dot_proto_dot_emulator__controller__pb2.PhoneResponse.SerializeToString), 'sendSms': grpc.unary_unary_rpc_method_handler(servicer.sendSms, request_deserializer=androidbox_dot_proto_dot_emulator__controller__pb2.SmsMessage.FromString, response_serializer=androidbox_dot_proto_dot_emulator__controller__pb2.PhoneResponse.SerializeToString), 'setPhoneNumber': grpc.unary_unary_rpc_method_handler(servicer.setPhoneNumber, request_deserializer=androidbox_dot_proto_dot_emulator__controller__pb2.PhoneNumber.FromString, response_serializer=androidbox_dot_proto_dot_emulator__controller__pb2.PhoneResponse.SerializeToString), 'getStatus': grpc.unary_unary_rpc_method_handler(servicer.getStatus, request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString, response_serializer=androidbox_dot_proto_dot_emulator__controller__pb2.EmulatorStatus.SerializeToString), 'getScreenshot': grpc.unary_unary_rpc_method_handler(servicer.getScreenshot, request_deserializer=androidbox_dot_proto_dot_emulator__controller__pb2.ImageFormat.FromString, response_serializer=androidbox_dot_proto_dot_emulator__controller__pb2.Image.SerializeToString), 'streamScreenshot': grpc.unary_stream_rpc_method_handler(servicer.streamScreenshot, request_deserializer=androidbox_dot_proto_dot_emulator__controller__pb2.ImageFormat.FromString, response_serializer=androidbox_dot_proto_dot_emulator__controller__pb2.Image.SerializeToString), 'streamAudio': grpc.unary_stream_rpc_method_handler(servicer.streamAudio, request_deserializer=androidbox_dot_proto_dot_emulator__controller__pb2.AudioFormat.FromString, response_serializer=androidbox_dot_proto_dot_emulator__controller__pb2.AudioPacket.SerializeToString), 'injectAudio': grpc.stream_unary_rpc_method_handler(servicer.injectAudio, request_deserializer=androidbox_dot_proto_dot_emulator__controller__pb2.AudioPacket.FromString, response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString), 'getMicrophoneState': grpc.unary_unary_rpc_method_handler(servicer.getMicrophoneState, request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString, response_serializer=androidbox_dot_proto_dot_emulator__controller__pb2.MicrophoneState.SerializeToString), 'setMicrophoneState': grpc.unary_unary_rpc_method_handler(servicer.setMicrophoneState, request_deserializer=androidbox_dot_proto_dot_emulator__controller__pb2.MicrophoneState.FromString, response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString), 'getLogcat': grpc.unary_unary_rpc_method_handler(servicer.getLogcat, request_deserializer=androidbox_dot_proto_dot_emulator__controller__pb2.LogMessage.FromString, response_serializer=androidbox_dot_proto_dot_emulator__controller__pb2.LogMessage.SerializeToString), 'streamLogcat': grpc.unary_stream_rpc_method_handler(servicer.streamLogcat, request_deserializer=androidbox_dot_proto_dot_emulator__controller__pb2.LogMessage.FromString, response_serializer=androidbox_dot_proto_dot_emulator__controller__pb2.LogMessage.SerializeToString), 'setVmState': grpc.unary_unary_rpc_method_handler(servicer.setVmState, request_deserializer=androidbox_dot_proto_dot_emulator__controller__pb2.VmRunState.FromString, response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString), 'getVmState': grpc.unary_unary_rpc_method_handler(servicer.getVmState, request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString, response_serializer=androidbox_dot_proto_dot_emulator__controller__pb2.VmRunState.SerializeToString), 'setDisplayConfigurations': grpc.unary_unary_rpc_method_handler(servicer.setDisplayConfigurations, request_deserializer=androidbox_dot_proto_dot_emulator__controller__pb2.DisplayConfigurations.FromString, response_serializer=androidbox_dot_proto_dot_emulator__controller__pb2.DisplayConfigurations.SerializeToString), 'getDisplayConfigurations': grpc.unary_unary_rpc_method_handler(servicer.getDisplayConfigurations, request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString, response_serializer=androidbox_dot_proto_dot_emulator__controller__pb2.DisplayConfigurations.SerializeToString), 'streamNotification': grpc.unary_stream_rpc_method_handler(servicer.streamNotification, request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString, response_serializer=androidbox_dot_proto_dot_emulator__controller__pb2.Notification.SerializeToString), 'rotateVirtualSceneCamera': grpc.unary_unary_rpc_method_handler(servicer.rotateVirtualSceneCamera, request_deserializer=androidbox_dot_proto_dot_emulator__controller__pb2.RotationRadian.FromString, response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString), 'setVirtualSceneCameraVelocity': grpc.unary_unary_rpc_method_handler(servicer.setVirtualSceneCameraVelocity, request_deserializer=androidbox_dot_proto_dot_emulator__controller__pb2.Velocity.FromString, response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString), 'setPosture': grpc.unary_unary_rpc_method_handler(servicer.setPosture, request_deserializer=androidbox_dot_proto_dot_emulator__controller__pb2.Posture.FromString, response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString), 'getBrightness': grpc.unary_unary_rpc_method_handler(servicer.getBrightness, request_deserializer=androidbox_dot_proto_dot_emulator__controller__pb2.BrightnessValue.FromString, response_serializer=androidbox_dot_proto_dot_emulator__controller__pb2.BrightnessValue.SerializeToString), 'setBrightness': grpc.unary_unary_rpc_method_handler(servicer.setBrightness, request_deserializer=androidbox_dot_proto_dot_emulator__controller__pb2.BrightnessValue.FromString, response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString), 'getDisplayMode': grpc.unary_unary_rpc_method_handler(servicer.getDisplayMode, request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString, response_serializer=androidbox_dot_proto_dot_emulator__controller__pb2.DisplayMode.SerializeToString), 'setDisplayMode': grpc.unary_unary_rpc_method_handler(servicer.setDisplayMode, request_deserializer=androidbox_dot_proto_dot_emulator__controller__pb2.DisplayMode.FromString, response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString), 'setXrOptions': grpc.unary_unary_rpc_method_handler(servicer.setXrOptions, request_deserializer=androidbox_dot_proto_dot_emulator__controller__pb2.XrOptions.FromString, response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString), 'getXrOptions': grpc.unary_unary_rpc_method_handler(servicer.getXrOptions, request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString, response_serializer=androidbox_dot_proto_dot_emulator__controller__pb2.XrOptions.SerializeToString), 'setEnvironment': grpc.unary_unary_rpc_method_handler(servicer.setEnvironment, request_deserializer=androidbox_dot_proto_dot_emulator__controller__pb2.Environment.FromString, response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString), 'getEnvironment': grpc.unary_unary_rpc_method_handler(servicer.getEnvironment, request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString, response_serializer=androidbox_dot_proto_dot_emulator__controller__pb2.Environment.SerializeToString), 'getHostCameras': grpc.unary_unary_rpc_method_handler(servicer.getHostCameras, request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString, response_serializer=androidbox_dot_proto_dot_emulator__controller__pb2.CameraList.SerializeToString)}
    generic_handler = grpc.method_handlers_generic_handler('android.emulation.control.EmulatorController', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('android.emulation.control.EmulatorController', rpc_method_handlers)

class EmulatorController:

    @staticmethod
    def streamSensor(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_stream(request, target, '/android.emulation.control.EmulatorController/streamSensor', androidbox_dot_proto_dot_emulator__controller__pb2.SensorValue.SerializeToString, androidbox_dot_proto_dot_emulator__controller__pb2.SensorValue.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def getSensor(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/android.emulation.control.EmulatorController/getSensor', androidbox_dot_proto_dot_emulator__controller__pb2.SensorValue.SerializeToString, androidbox_dot_proto_dot_emulator__controller__pb2.SensorValue.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def setSensor(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/android.emulation.control.EmulatorController/setSensor', androidbox_dot_proto_dot_emulator__controller__pb2.SensorValue.SerializeToString, google_dot_protobuf_dot_empty__pb2.Empty.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def setPhysicalModel(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/android.emulation.control.EmulatorController/setPhysicalModel', androidbox_dot_proto_dot_emulator__controller__pb2.PhysicalModelValue.SerializeToString, google_dot_protobuf_dot_empty__pb2.Empty.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def getPhysicalModel(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/android.emulation.control.EmulatorController/getPhysicalModel', androidbox_dot_proto_dot_emulator__controller__pb2.PhysicalModelValue.SerializeToString, androidbox_dot_proto_dot_emulator__controller__pb2.PhysicalModelValue.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def streamPhysicalModel(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_stream(request, target, '/android.emulation.control.EmulatorController/streamPhysicalModel', androidbox_dot_proto_dot_emulator__controller__pb2.PhysicalModelValue.SerializeToString, androidbox_dot_proto_dot_emulator__controller__pb2.PhysicalModelValue.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def setClipboard(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/android.emulation.control.EmulatorController/setClipboard', androidbox_dot_proto_dot_emulator__controller__pb2.ClipData.SerializeToString, google_dot_protobuf_dot_empty__pb2.Empty.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def getClipboard(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/android.emulation.control.EmulatorController/getClipboard', google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, androidbox_dot_proto_dot_emulator__controller__pb2.ClipData.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def streamClipboard(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_stream(request, target, '/android.emulation.control.EmulatorController/streamClipboard', google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, androidbox_dot_proto_dot_emulator__controller__pb2.ClipData.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def setBattery(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/android.emulation.control.EmulatorController/setBattery', androidbox_dot_proto_dot_emulator__controller__pb2.BatteryState.SerializeToString, google_dot_protobuf_dot_empty__pb2.Empty.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def getBattery(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/android.emulation.control.EmulatorController/getBattery', google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, androidbox_dot_proto_dot_emulator__controller__pb2.BatteryState.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def setGps(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/android.emulation.control.EmulatorController/setGps', androidbox_dot_proto_dot_emulator__controller__pb2.GpsState.SerializeToString, google_dot_protobuf_dot_empty__pb2.Empty.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def getGps(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/android.emulation.control.EmulatorController/getGps', google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, androidbox_dot_proto_dot_emulator__controller__pb2.GpsState.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def sendFingerprint(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/android.emulation.control.EmulatorController/sendFingerprint', androidbox_dot_proto_dot_emulator__controller__pb2.Fingerprint.SerializeToString, google_dot_protobuf_dot_empty__pb2.Empty.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def sendKey(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/android.emulation.control.EmulatorController/sendKey', androidbox_dot_proto_dot_emulator__controller__pb2.KeyboardEvent.SerializeToString, google_dot_protobuf_dot_empty__pb2.Empty.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def sendTouch(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/android.emulation.control.EmulatorController/sendTouch', androidbox_dot_proto_dot_emulator__controller__pb2.TouchEvent.SerializeToString, google_dot_protobuf_dot_empty__pb2.Empty.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def sendMouse(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/android.emulation.control.EmulatorController/sendMouse', androidbox_dot_proto_dot_emulator__controller__pb2.MouseEvent.SerializeToString, google_dot_protobuf_dot_empty__pb2.Empty.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def injectWheel(request_iterator, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.stream_unary(request_iterator, target, '/android.emulation.control.EmulatorController/injectWheel', androidbox_dot_proto_dot_emulator__controller__pb2.WheelEvent.SerializeToString, google_dot_protobuf_dot_empty__pb2.Empty.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def streamInputEvent(request_iterator, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.stream_unary(request_iterator, target, '/android.emulation.control.EmulatorController/streamInputEvent', androidbox_dot_proto_dot_emulator__controller__pb2.InputEvent.SerializeToString, google_dot_protobuf_dot_empty__pb2.Empty.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def sendPhone(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/android.emulation.control.EmulatorController/sendPhone', androidbox_dot_proto_dot_emulator__controller__pb2.PhoneCall.SerializeToString, androidbox_dot_proto_dot_emulator__controller__pb2.PhoneResponse.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def sendSms(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/android.emulation.control.EmulatorController/sendSms', androidbox_dot_proto_dot_emulator__controller__pb2.SmsMessage.SerializeToString, androidbox_dot_proto_dot_emulator__controller__pb2.PhoneResponse.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def setPhoneNumber(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/android.emulation.control.EmulatorController/setPhoneNumber', androidbox_dot_proto_dot_emulator__controller__pb2.PhoneNumber.SerializeToString, androidbox_dot_proto_dot_emulator__controller__pb2.PhoneResponse.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def getStatus(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/android.emulation.control.EmulatorController/getStatus', google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, androidbox_dot_proto_dot_emulator__controller__pb2.EmulatorStatus.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def getScreenshot(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/android.emulation.control.EmulatorController/getScreenshot', androidbox_dot_proto_dot_emulator__controller__pb2.ImageFormat.SerializeToString, androidbox_dot_proto_dot_emulator__controller__pb2.Image.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def streamScreenshot(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_stream(request, target, '/android.emulation.control.EmulatorController/streamScreenshot', androidbox_dot_proto_dot_emulator__controller__pb2.ImageFormat.SerializeToString, androidbox_dot_proto_dot_emulator__controller__pb2.Image.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def streamAudio(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_stream(request, target, '/android.emulation.control.EmulatorController/streamAudio', androidbox_dot_proto_dot_emulator__controller__pb2.AudioFormat.SerializeToString, androidbox_dot_proto_dot_emulator__controller__pb2.AudioPacket.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def injectAudio(request_iterator, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.stream_unary(request_iterator, target, '/android.emulation.control.EmulatorController/injectAudio', androidbox_dot_proto_dot_emulator__controller__pb2.AudioPacket.SerializeToString, google_dot_protobuf_dot_empty__pb2.Empty.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def getMicrophoneState(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/android.emulation.control.EmulatorController/getMicrophoneState', google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, androidbox_dot_proto_dot_emulator__controller__pb2.MicrophoneState.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def setMicrophoneState(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/android.emulation.control.EmulatorController/setMicrophoneState', androidbox_dot_proto_dot_emulator__controller__pb2.MicrophoneState.SerializeToString, google_dot_protobuf_dot_empty__pb2.Empty.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def getLogcat(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/android.emulation.control.EmulatorController/getLogcat', androidbox_dot_proto_dot_emulator__controller__pb2.LogMessage.SerializeToString, androidbox_dot_proto_dot_emulator__controller__pb2.LogMessage.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def streamLogcat(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_stream(request, target, '/android.emulation.control.EmulatorController/streamLogcat', androidbox_dot_proto_dot_emulator__controller__pb2.LogMessage.SerializeToString, androidbox_dot_proto_dot_emulator__controller__pb2.LogMessage.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def setVmState(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/android.emulation.control.EmulatorController/setVmState', androidbox_dot_proto_dot_emulator__controller__pb2.VmRunState.SerializeToString, google_dot_protobuf_dot_empty__pb2.Empty.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def getVmState(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/android.emulation.control.EmulatorController/getVmState', google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, androidbox_dot_proto_dot_emulator__controller__pb2.VmRunState.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def setDisplayConfigurations(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/android.emulation.control.EmulatorController/setDisplayConfigurations', androidbox_dot_proto_dot_emulator__controller__pb2.DisplayConfigurations.SerializeToString, androidbox_dot_proto_dot_emulator__controller__pb2.DisplayConfigurations.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def getDisplayConfigurations(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/android.emulation.control.EmulatorController/getDisplayConfigurations', google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, androidbox_dot_proto_dot_emulator__controller__pb2.DisplayConfigurations.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def streamNotification(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_stream(request, target, '/android.emulation.control.EmulatorController/streamNotification', google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, androidbox_dot_proto_dot_emulator__controller__pb2.Notification.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def rotateVirtualSceneCamera(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/android.emulation.control.EmulatorController/rotateVirtualSceneCamera', androidbox_dot_proto_dot_emulator__controller__pb2.RotationRadian.SerializeToString, google_dot_protobuf_dot_empty__pb2.Empty.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def setVirtualSceneCameraVelocity(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/android.emulation.control.EmulatorController/setVirtualSceneCameraVelocity', androidbox_dot_proto_dot_emulator__controller__pb2.Velocity.SerializeToString, google_dot_protobuf_dot_empty__pb2.Empty.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def setPosture(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/android.emulation.control.EmulatorController/setPosture', androidbox_dot_proto_dot_emulator__controller__pb2.Posture.SerializeToString, google_dot_protobuf_dot_empty__pb2.Empty.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def getBrightness(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/android.emulation.control.EmulatorController/getBrightness', androidbox_dot_proto_dot_emulator__controller__pb2.BrightnessValue.SerializeToString, androidbox_dot_proto_dot_emulator__controller__pb2.BrightnessValue.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def setBrightness(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/android.emulation.control.EmulatorController/setBrightness', androidbox_dot_proto_dot_emulator__controller__pb2.BrightnessValue.SerializeToString, google_dot_protobuf_dot_empty__pb2.Empty.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def getDisplayMode(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/android.emulation.control.EmulatorController/getDisplayMode', google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, androidbox_dot_proto_dot_emulator__controller__pb2.DisplayMode.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def setDisplayMode(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/android.emulation.control.EmulatorController/setDisplayMode', androidbox_dot_proto_dot_emulator__controller__pb2.DisplayMode.SerializeToString, google_dot_protobuf_dot_empty__pb2.Empty.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def setXrOptions(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/android.emulation.control.EmulatorController/setXrOptions', androidbox_dot_proto_dot_emulator__controller__pb2.XrOptions.SerializeToString, google_dot_protobuf_dot_empty__pb2.Empty.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def getXrOptions(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/android.emulation.control.EmulatorController/getXrOptions', google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, androidbox_dot_proto_dot_emulator__controller__pb2.XrOptions.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def setEnvironment(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/android.emulation.control.EmulatorController/setEnvironment', androidbox_dot_proto_dot_emulator__controller__pb2.Environment.SerializeToString, google_dot_protobuf_dot_empty__pb2.Empty.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def getEnvironment(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/android.emulation.control.EmulatorController/getEnvironment', google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, androidbox_dot_proto_dot_emulator__controller__pb2.Environment.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def getHostCameras(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/android.emulation.control.EmulatorController/getHostCameras', google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, androidbox_dot_proto_dot_emulator__controller__pb2.CameraList.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)
