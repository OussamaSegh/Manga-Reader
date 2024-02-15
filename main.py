import os
import json
import requests
import img2pdf as pdf
import webbrowser as wb

# Define API endpoints
search_url = "https://dramalama-api.vercel.app/manga/mangadex/{}"
info_url = "https://dramalama-api.vercel.app/manga/mangadex/info/{}"
pages_url = "https://dramalama-api.vercel.app/manga/mangadex/read/{}"

# Function to search for manga
def search_manga():
    user_input = input("What manga would you like to search for: ")
    data = requests.get(search_url.format(user_input)).json()

    with open("jsons/manga.json", "w") as file:
        json.dump(data, file)
    
    with open("jsons/manga.json", "r") as file:
        fetched_mangas = json.load(file)["results"]

    for i, j in enumerate(fetched_mangas, start=1):
        try:
            print(f"Manga Entry {i}")
            print(f"\033[1mTitle\033[0m: {j['title']}")
            print(f"\033[1mAlt title\033[0m: {', '.join(x for i in j['altTitles'] for x in i.values())}")
            print(f"\033[1mRelease year\033[0m: {j['releaseDate']}")
            print(f"\033[1mStatus\033[0m: {j['status']}")
            print(f"\033[1mDescription\033[0m: {j['description'].strip()}")
            print("\n================================\n")
        except KeyError:
            pass
    
    manga_info(fetched_mangas)

# Function to fetch manga information
def manga_info(data):
    try:
        user_choice = int(input("Enter the manga entry no. of the manga you would like to read: "))
        manga_id = data[user_choice - 1]["id"]
    except:
        print("Some error occurred. Please try again.")
        exit()

    manga_info = requests.get(info_url.format(manga_id)).json()
    with open("jsons/manga_info.json", "w") as file:
        json.dump(manga_info, file)
    
    os.system("cls")
    with open("jsons/manga_info.json", "r") as file:
        data = json.load(file)
        dc = data["chapters"]

    print("Selected Manga is: ")
    try:
        print(f"\033[1mTitle\033[0m: {data['title']}")
        print(f"\033[1mDescription\033[0m: {data['description']['en']}")
        print(f"\033[1mGenres\033[0m: {', '.join(i for i in data['genres'])}")
        print(f"\033[1mThemes\033[0m: {', '.join(i for i in data['themes'])}")
        print(f"\033[1mRelease year\033[0m: {data['releaseDate']}")
    except KeyError:
        pass

    print("\nFollowing Chapters were found:\n")


    for j in (reversed(dc)):
        print(f"Chapter Name: {j["title"]}")
        print(f"Chapter Number: {j["chapterNumber"]}")
        print(f"Volume Number: {j["volumeNumber"]}")
        print(f"Number of pages: {j["pages"]}")
        print("\n================================\n")
    
    try:
        user_opt = input("Enter the chapter number of the manga that you would like to read: ")
        chapter_id = [i["id"] for i in dc if ((i["chapterNumber"] == user_opt) if i["chapterNumber"] is not None else True) and i["pages"] != 0][0]
    except Exception as e:
        print(e)
        print("Some error occurred. Please try again.")
        exit()

    folder_name = [f"{data['title']}_{i["title"]}_Chapter-{i["chapterNumber"]}_Vol-{i["volumeNumber"]}" for i in dc if i["id"] == chapter_id][0]

    get_mangas(chapter_id, folder_name)

# Function to fetch manga images and convert them to PDF
def get_mangas(chapter_id, folder_name):

    if os.path.exists(os.path.join("cache", "images", folder_name)):
        print("Looks like the files are already there.\nTrying to convert them to pdf.")
        convert_to_pdf(folder_name)
    else:
        os.makedirs(os.path.join("cache", "images", folder_name))
        print("Folder created successfully")

    data = requests.get(pages_url.format(chapter_id)).json()
    with open("jsons/manga_links.json", "w") as file:
        json.dump(data, file)

    with open("jsons/manga_links.json", "r") as file:
        manga_data = json.load(file)

    manga_urls = [i["img"] for i in manga_data]
    for i, j in enumerate(manga_urls, start=1):
        download_images(j, folder_name, i)
    
    convert_to_pdf(folder_name)

# Function to download manga images
def download_images(url, foldername, filename):

    response = requests.get(url)
    with open(f"cache/images/{foldername}/{str(filename)}.png", "wb") as file:
        file.write(response.content)

# Function to convert images to PDF
def convert_to_pdf(folder_name):

    if os.path.exists(os.path.join(os.curdir, "cache", "pdf", f"{folder_name}.pdf")):
        print("PDF is already present")
    else:
        image_files = [i for i in os.listdir(f"cache/images/{folder_name}") if os.path.isfile(f"cache/images/{folder_name}/{i}")]
        sorted_files = sorted(image_files, key=lambda x: int(x.split('.')[0]))
        
        with open(os.path.join(os.curdir, "cache", "pdf", f"{folder_name}.pdf"), "wb") as file:
            file.write(pdf.convert([os.path.join("cache", "images", folder_name, f) for f in sorted_files]))

    wb.open_new_tab(os.path.join(os.curdir, "cache", "pdf", f"{folder_name}.pdf"))
    exit()	

# Set the current directory to where the script is located
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Call the search_manga function to start the program
search_manga()
