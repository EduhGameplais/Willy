using Mighty;
using Pv;

namespace Willy;

public class WakeWord
{
    public delegate void WakeWordCallback();

    private readonly string _engine;
    private readonly string _model;
    private readonly string _accessKey;

    private readonly PvRecorder _recorder;
    private readonly Porcupine _porcupine;
    public WakeWord(dynamic wakeWordConfig)
    {
        _engine = (string)wakeWordConfig.Engine;

        switch (_engine.ToLower())
        {
            case "porcupine":
                _recorder = PvRecorder.Create(512);
                _porcupine = Porcupine.FromKeywordPaths(
                    (string)wakeWordConfig.Porcupine.AccessKey,
            new List<string> {(string)wakeWordConfig.Porcupine.ModelPath});
                break;
            default:
                throw new Exception($"Unknown WakeWord engine: {_engine}");
        }
    }
    
    private bool _detectEnabled = true;
    
    public void DetectWakeWordLoop(WakeWordCallback callback)
    {
        switch (_engine.ToLower())
        {
            case "porcupine":
                _recorder.Start();
                Log.PrintLn("$Yellow$Aguardando wake word...");
        
                while (_recorder.IsRecording) {
                    short[] audioFrame = _recorder.Read();
                    int keywordIndex = _porcupine.Process(audioFrame);
                    if (keywordIndex >= 0) {
                        Log.PrintLn("$Green$Wake word detectado!");
                        callback();
                    }
                }
                break;
        }
    }

    public void StopWakeWordLoop()
    {
        _recorder.Stop();
        Log.PrintLn("$Purple$Detecção de wake word parada.");
    }
}