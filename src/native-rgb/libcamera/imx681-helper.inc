/* IMX681 raw gain code is independently established by the active SP11
 * sensor callback and the native driver. No assumed black pedestal is added.
 */
class CameraSensorHelperImx681 : public CameraSensorHelper
{
public:
    CameraSensorHelperImx681()
    {
        gain_ = AnalogueGainLinear{ 0, 1024, -1, 1024 };
    }
};
REGISTER_CAMERA_SENSOR_HELPER("imx681", CameraSensorHelperImx681)

