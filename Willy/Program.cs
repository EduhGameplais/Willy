using Mighty;
using Newtonsoft.Json;
using OllamaSharp;
using OllamaSharp.Models.Chat;

namespace Willy;

class Program
{
    static void Main(string[] args)
    {
        Log.LogFormat = Log.ServerLogFormat;
        
        dynamic config = Config.LoadConfig("Config/config.json");
        
        SpeechToText speechToText = new SpeechToText("/home/edu/Downloads/ggml-large-v3-turbo-q8_0.bin");
        WakeWord wakeWord = new WakeWord("/home/edu/Downloads/Oi-Willy_en_linux_v3_0_0/Oi-Willy_en_linux_v3_0_0.ppn",
            "HTNEKETuTaM6+BHhtpD9B+hCbjUCWUVjV9BMd2t7wjtPP7EkB41f2Q==");
        
        Log.PrintLn("$Yellow$Carregando Ollama...");
        var uri = new Uri((string)config.LanguageModel.ProviderUrl);
        var ollama = new OllamaApiClient(uri);
            
        ollama.SelectedModel = config.LanguageModel.Model;

        //ollama.PullModelAsync(config.ollama.model);
        
        var chat = new Chat(ollama);
        
        
        
        string sysprompt = String.Empty;
        try
        {
            foreach (var line in config.LanguageModel.Prompt)
            {
                sysprompt += line + "\n";
            }
        }
        catch (Exception ex)
        {
            Log.PrintError(ex, "Campo \"prompt\" não foi encontrado no arquivo de configuração.");
            return;
        }
        
        chat.Messages.Add( new Message(ChatRole.System, sysprompt));
        
        Log.PrintLn("$Green$Ollama Carregado.");
        
        wakeWord.DetectWakeWordLoop(async () =>
        {
            AudioRecorder recorder = new AudioRecorder("/home/edu/Desktop/audio.wav", 
                (float)config.Audio.AudioRecorder.SilenceThreshold, 
                (int)config.Audio.AudioRecorder.SilenceDurationMs);

            recorder.StartRecordingAsync().GetAwaiter().GetResult();

            var asa = "/home/edu/Desktop/audio.wav";

            var transcription = speechToText.GetTextFromFile(asa);
            string imagePath = "/home/edu/Downloads/arvore.jpg";
            byte[] imageBytes = await File.ReadAllBytesAsync(imagePath);
            string base64Image = Convert.ToBase64String(imageBytes);
            
            //chat.Messages.Add(new Message(ChatRole.User, new string[]{base64Image}));
            await foreach (var answerToken in chat.SendAsync(transcription))
                Console.Write(answerToken);
        });



        //1° Detectar a voz e transcrever - Whisper.NET - 85% --Fazer a gravação antes de detectar a voz, para a pessoa poder falar "Oi Willy" e logo em seguida já começar a falar, sem esperar ser detectado.

        //2° Criar resposta - Gemma3:12b Google Colab -Partially

        //3° Falar a resposta
    }
}