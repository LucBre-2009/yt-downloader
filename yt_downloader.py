import os
import tempfile
import zipfile
import urllib.request
import shutil
from tkinter import Tk, filedialog
from yt_dlp import YoutubeDL
import time


# ---------------- FFmpeg functions ----------------

def ensure_ffmpeg():

    script_dir = os.path.dirname(os.path.abspath(__file__))
    zip_name = "ffmpeg-8.0.1-essentials_build.zip"
    local_zip = os.path.join(script_dir, zip_name)

    tmp_dir = tempfile.gettempdir()
    ffmpeg_dir = os.path.join(tmp_dir, "ffmpeg_temp")
    ffmpeg_path = os.path.join(ffmpeg_dir, "ffmpeg.exe")

    downloaded_by_script = False


    if os.path.isfile(local_zip):

        print("FFmpeg is already installed. Download will start shortly...")
        zip_path = local_zip

    else:

        print("FFmpeg is being downloaded and installed temporarily...")

        url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
        zip_path = os.path.join(tmp_dir, zip_name)

        urllib.request.urlretrieve(url, zip_path)

        downloaded_by_script = True


    with zipfile.ZipFile(zip_path, 'r') as zip_ref:

        zip_ref.extractall(ffmpeg_dir)


    for root, dirs, files in os.walk(ffmpeg_dir):

        if "ffmpeg.exe" in files:

            ffmpeg_path = os.path.join(root, "ffmpeg.exe")
            break


    if downloaded_by_script:

        os.remove(zip_path)
        print("FFmpeg download completed.")


    return ffmpeg_path, ffmpeg_dir, downloaded_by_script



def cleanup_ffmpeg(ffmpeg_dir, downloaded_by_script):

    if downloaded_by_script and os.path.exists(ffmpeg_dir):

        shutil.rmtree(ffmpeg_dir)
        print("FFmpeg temporary files were removed.")

    else:

        print("FFmpeg remains installed since it was provided by the user.")



# ---------------- choose folder ----------------

def choose_folder():

    Tk().withdraw()
    folder = filedialog.askdirectory(title="Choose a save folder...")
    return folder



# ---------------- bulk input ----------------

def get_bulk_links():

    print("\nEnter links (blank line to start download):")
    print("Press Enter after each link, and leave a blank line to begin.\n")

    links = []

    while True:

        link = input("> ").strip()

        if link == "":
            break

        links.append(link)

    return links



# ---------------- main program ----------------

def main():
    print("Welcome to the YT Downloader!\n")

    print("Choose quality:\n480p=1; 720p=2; 1080p=3; 1440p=4; 4k=5")

    qual = input("> ")

    quality_map = {

        '1': '480',
        '2': '720',
        '3': '1080',
        '4': '1440',
        '5': '2160'

    }

    qual_str = quality_map.get(qual, '1080')

    vp = input("Video, Playlist or Bulk (V/P/B): ").lower()

    is_playlist = vp == 'p'
    is_bulk = vp == 'b'

    if is_bulk:

        urls = get_bulk_links()

    else:

        url = input("Enter link: ")
        urls = [url]


    numbering = 'n'

    if is_playlist or is_bulk:

        numbering = input("Enable numbering? (Y/N): ").lower()


    download_folder = choose_folder()

    temp_folder = os.path.join(download_folder, "DONT_TOUCH_TEMP")

    os.makedirs(temp_folder, exist_ok=True)


    ffmpeg_path, ffmpeg_dir, downloaded_by_script = ensure_ffmpeg()


    if numbering == 'y':

        outtmpl = os.path.join(

            temp_folder,
            '%(autonumber)03d - %(title)s.%(ext)s'

        )

    else:

        outtmpl = os.path.join(

            temp_folder,
            '%(title)s.%(ext)s'

        )


    ydl_opts = {

        'format': f'bestvideo[height={qual_str}]+bestaudio/best[height={qual_str}]/bestvideo[height={qual_str}]+bestaudio/best',

        'merge_output_format': 'mp4',

        'ffmpeg_location': ffmpeg_path,

        'outtmpl': outtmpl,

        'noplaylist': not is_playlist,

        'ignoreerrors': True,

        'quiet': True,

        'no_warnings': True,

    }


    print("\nStarting download...\n")


    with YoutubeDL(ydl_opts) as ydl:

        if is_bulk:

            for url in urls:

                print("Download:", url)
                ydl.download([url])

        else:

            ydl.download(urls)



    for file in os.listdir(temp_folder):

        if file.endswith(".mp4"):

            shutil.move(

                os.path.join(temp_folder, file),

                os.path.join(download_folder, file)

            )


    shutil.rmtree(temp_folder, ignore_errors=True)


    cleanup_ffmpeg(ffmpeg_dir, downloaded_by_script)


    print("\nDone!")
    print("All videos have been saved to the selected folder.")


    time.sleep(5)



if __name__ == "__main__":

    main()
