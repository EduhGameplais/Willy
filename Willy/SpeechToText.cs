using Whisper.net;
using Mighty;

namespace Willy;

public class SpeechToText
{
    private WhisperProcessor _processor;

    private string _tempOutput = string.Empty;
    
    private string _modelPath = string.Empty;
    private string _engine = string.Empty;
    
    public SpeechToText(dynamic sttConfig, string device="cuda")
    {
        _engine = (string)sttConfig.Engine;

        switch (_engine.ToLower())
        {
            case "whisper" or "whisper.net":
                _modelPath = (string)sttConfig.Whisper.ModelPath;
                
                var runtimeType = device == "cuda" ? "GPU" : "CPU";
                Log.PrintLn($"$Yellow$Carregando Whisper... ({runtimeType})");
                var whisperFactory = WhisperFactory.FromPath(_modelPath, new WhisperFactoryOptions
                {
                    UseGpu = device.ToLower() == "cuda" // Ativa o uso de GPU
                });
                _processor = whisperFactory.CreateBuilder()
                    .WithLanguage("pt")
                    .WithSingleSegment()
                    .WithSegmentEventHandler((segment) =>
                    {
                        _tempOutput = segment.Text;
                    })
                    .Build();
                Log.PrintLn("$Green$Whisper Carregado!");
                break;
            default:
                throw new Exception($"Unknown STT engine: {_engine}");
        }
    }

    public string GetTextFromFile(string wavFile)
    {
        Log.PrintLn($"$Yellow$Transcrevendo {wavFile}...");
        switch (_engine.ToLower())
        {
            case "whisper" or "whisper.net":
            {
                using var fileStream = File.OpenRead(wavFile);

                _processor.Process(fileStream);
                Log.PrintLn($"$Green$Transcrição: {_tempOutput}");
                return _tempOutput;
            }
            default:
                return null;
        }
    }
}