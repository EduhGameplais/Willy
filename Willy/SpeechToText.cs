using Whisper.net;
using Mighty;

namespace Willy;

public class SpeechToText
{
    private WhisperProcessor _processor;

    private string _tempOutput = string.Empty;
    
    public SpeechToText(string modelPath, string device="cuda")
    {
        var runtimeType = device == "cuda" ? "GPU" : "CPU";
        Log.PrintLn($"$Yellow$Carregando Whisper... ({runtimeType})");
        var whisperFactory = WhisperFactory.FromPath(modelPath, new WhisperFactoryOptions
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
    }

    public string GetTextFromFile(string wavFile)
    {
        Log.PrintLn($"$Yellow$Transcrevendo {wavFile}...");
        using var fileStream = File.OpenRead(wavFile);

        _processor.Process(fileStream);
        Log.PrintLn($"$Green$Transcrição: {_tempOutput}");
        return _tempOutput;
    }
}