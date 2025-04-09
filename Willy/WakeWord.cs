using Mighty;
using Pv;

namespace Willy;

public class WakeWord(string modelPath, string accessKey)
{
    public delegate void WakeWordCallback();

    private readonly PvRecorder _recorder = PvRecorder.Create(512);
    private readonly Porcupine _porcupine = Porcupine.FromKeywordPaths(
        accessKey,
        new List<string> {modelPath});
    private bool _detectEnabled = true;
    
    public void DetectWakeWordLoop(WakeWordCallback callback)
    {
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
    }

    public void StopWakeWordLoop()
    {
        _recorder.Stop();
        Log.PrintLn("$Purple$Detecção de wake word parada.");
    }
}