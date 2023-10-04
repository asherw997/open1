import requests
from bs4 import BeautifulSoup
from io import BytesIO
from PIL import Image
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import tempfile
import os
from urllib.parse import urljoin

# Define the URL of the manga chapter page
chapter_url = input("Enter the URL of the manga chapter page: ")

# Define the PDF file name
pdf_filename = input("Enter the PDF file name (including .pdf extension): ")

# Send an HTTP GET request to the chapter URL
response = requests.get(chapter_url)
soup = BeautifulSoup(response.text, 'html.parser')

# Define a custom function to filter images based on your criteria
def is_desired_image(img_tag):
    if 'data-next-image' in img_tag.attrs:
        img_srcset = img_tag['srcset']
        # Check if the image source contains the desired format
        return 'cdn.sanity.io' in img_tag['data-next-image'] and 'png' in img_srcset
    return False

# Find image elements that meet your criteria
image_tags = soup.find_all(is_desired_image)

# Create a PDF file
pdf = canvas.Canvas(pdf_filename, pagesize=letter)

# Create a temporary directory to save image files
temp_dir = tempfile.mkdtemp()

# Loop through the image tags and download desired images
for i, img_tag in enumerate(image_tags):
    img_url = img_tag['data-next-image']

    # Handle relative URLs by joining them with the base URL
    img_url = urljoin(chapter_url, img_url)

    # Download the image
    img_response = requests.get(img_url)
    img_data = BytesIO(img_response.content)
    img = Image.open(img_data)

    # Convert the image to RGB mode if it's RGBA
    if img.mode == 'RGBA':
        img = img.convert('RGB')

    # Save the image to a temporary file as JPEG
    img_file_path = os.path.join(temp_dir, f"image_{i}.jpg")
    img.save(img_file_path, 'JPEG')

    # Set the size of the image on the PDF page (you may need to adjust the size)
    img_width, img_height = img.size
    pdf.drawImage(img_file_path, 0, 0, width=img_width, height=img_height)

    # Add a new page for the next image (optional)
    if i < len(image_tags) - 1:
        pdf.showPage()

# Save the PDF
pdf.save()

# Clean up temporary image files
for i in range(len(image_tags)):
    img_file_path = os.path.join(temp_dir, f"image_{i}.jpg")
    os.remove(img_file_path)

# Remove the temporary directory
os.rmdir(temp_dir)

print(f"PDF saved as {pdf_filename}")
