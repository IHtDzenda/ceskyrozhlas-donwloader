using System;
using System.Diagnostics;
using System.Text.RegularExpressions;

namespace MyApp
{
  internal class Program
  {
    private static async Task Main(string[] args)
    {
      Console.Write("Enter url\n=>");
      string inputedUrl = Console.ReadLine();

      Uri uri = new Uri(inputedUrl);
      string name = uri.Segments[uri.Segments.Length - 1].Replace("-", " ");

      List<string> urls = new List<string>(await GetLinks(inputedUrl));
      Console.WriteLine($"Found: {urls.Count}");

      List<Link> streams = new List<Link>(await GetStream(urls));
      streams.Sort((x, y) => x.Part.CompareTo(y.Part));
      foreach (Link link in streams)
      {
        await Task.Run(
            () =>
                Donwolad(
                    link.Url,
                    $"{name.Replace(" ", "_")}_{link.Part}-{streams.Count + 1}"
                )
        );
      }
    }

    public static async Task<List<string>> GetLinks(string url)
    {
      Uri uri = new Uri(url);
      string path = uri.AbsolutePath;
      path = Regex.Replace(path, @"[\d]", string.Empty);

      if (!path.EndsWith("-"))
      {
        path = path + "-";
      }
      List<string> urls = new List<string>();

      using (HttpClient client = new HttpClient())
      {
        client.BaseAddress = new Uri(url);
        HttpResponseMessage response = await client.GetAsync(url);
        Stream stream = await response.Content.ReadAsStreamAsync();
        StreamReader reader = new StreamReader(stream);
        string content = await reader.ReadToEndAsync();

        string pattern = @"<a href=.(.*). class=.m-chapters__link..*>";
        RegexOptions options = RegexOptions.Multiline;
        foreach (Match m in Regex.Matches(content, pattern, options))
        {
          if (m.Success)
          {
            string firstGroup = m.Groups[1].Value;
            Console.WriteLine(firstGroup);
            if (Uri.TryCreate("https://www.mujrozhlas.cz" + firstGroup, UriKind.Absolute, out Uri resultUri))
            {
              if (!urls.Contains(resultUri.AbsoluteUri))
              {
                urls.Add(resultUri.AbsoluteUri);
              }
            }
          }
        }
      }
      string input = url.Substring(url.Length - 1);

      if (int.TryParse(input, out int res))
      {
        urls.Add(url.Substring(0, url.Length - 8));
      }

      if (urls.Count == 0)
      {
        Console.WriteLine("No links found");
        return null;
      }
      url.Remove(url.Length - 1);
      return urls;
    }

    public static async Task<List<Link>> GetStream(List<string> urls)
    {
      string prefix = "https://api.mujrozhlas.cz/episodes/";
      List<string> apiId = new List<string>();
      List<Link> streams = new List<Link>();
      foreach (string url in urls)
      {
        using (HttpClient client = new HttpClient())
        {
          client.BaseAddress = new Uri(url);
          HttpResponseMessage response = await client.GetAsync(url);
          Stream stream = await response.Content.ReadAsStreamAsync();
          StreamReader reader = new StreamReader(stream);
          string content = await reader.ReadToEndAsync();
          RegexOptions options = RegexOptions.Multiline;
          string pattern = @"contentId...[a-zA-Z0-9\-]*.";

          foreach (Match m in Regex.Matches(content, pattern, options))
          {
            apiId.Add(m.Value.Replace("\"", "").Replace("contentId:", ""));
          }
        }
      }
      foreach (string id in apiId)
      {
        using (HttpClient client = new HttpClient())
        {
          client.BaseAddress = new Uri(prefix + id);
          HttpResponseMessage response = await client.GetAsync(prefix + id);
          Stream stream = await response.Content.ReadAsStreamAsync();
          StreamReader reader = new StreamReader(stream);
          string content = await reader.ReadToEndAsync();
          Match u = Regex.Match(content, @"https.....croaod.cz.*.mpd");
          int part = 0;

          if (
              int.TryParse(Regex.Match(content, @"part.:(\d*)").Groups[1].Value, out part)
          ) { }

          streams.Add(new Link { Part = part, Url = u.Value.Replace("\\", "") });
          Console.Write($"Part: {part} stream: {u.Value}\n");
        }
      }
      return streams;
    }

    public static async Task Donwolad(string link, string name)
    {
      string args = $"-i \"{link}\" -c:v copy -c:a libmp3lame -q:a 4 \"{name + ".mp3"}\" ";

      Process process = new Process();
      ProcessStartInfo startInfo = new ProcessStartInfo
      {
        FileName = "ffmpeg",
        Arguments = args,
        RedirectStandardOutput = true,
        RedirectStandardError = true,
        UseShellExecute = false,
        CreateNoWindow = true,
      };

      process.StartInfo = startInfo;
      process.OutputDataReceived += (sender, e) => Console.WriteLine(e.Data);
      process.ErrorDataReceived += (sender, e) => Console.WriteLine(e.Data);

      process.Start();
      process.BeginOutputReadLine();
      process.BeginErrorReadLine();
      process.WaitForExit();
      Console.WriteLine($"Done {name}");
    }

    public class Link
    {
      public int Part { get; set; }
      public string Url { get; set; }
    }
  }
}
