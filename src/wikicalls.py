import requests
import json
from PIL import Image
from io import BytesIO
from urllib import parse

# Save an individual image
def save_im(filename, headers):
    
    # Get the preferred url
    BASE = 'https://api.wikimedia.org/core/v1/commons/file/'
    url = BASE + filename
    response = requests.get(url, headers=headers)
    response = json.loads(response.text)
    preferred_file_url = response['preferred']['url']

    # Get the PIL image
    im_response = requests.get(preferred_file_url, headers=headers)
    img = Image.open(BytesIO(im_response.content))

    # Convert the image to a proper format and save it
    save_name = parse.quote_plus(filename[5:len(filename)])
    rgb_img = img.convert("RGB")
    rgb_img.save('files/images/' + save_name)

# Save a series of images
def get_images(sess, endpoint, page, headers, max_ims):
    
    # Query parameters
    PARAMS = {
        "action": "query",
        "format": "json",
        "titles": page,
        "prop": "images",
        "imlimit": str(max_ims)
    }

    # Load in data
    R = sess.get(url=endpoint, params=PARAMS)
    DATA = R.json()
    PAGES = DATA['query']['pages']

    with open('json/data.json', 'w') as f:
        json.dump(DATA, f)

    # Get image file names
    for k, v in PAGES.items():
        for img in v['images']:
            file = img['title']

            print(file)
            # Make sure that the file saves properly
            try:
                if file.split(".")[1] != 'gif' and file.split(".")[1] != 'tif': 
                    save_im(file, headers)
            except:
                print("Error: could not save " + file)