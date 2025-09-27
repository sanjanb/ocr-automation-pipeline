"""
Create sample test documents for OCR testing
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_sample_document(filename, title, fields, size=(800, 600)):
    """Create a sample document image with text"""
    
    # Create image with white background
    img = Image.new('RGB', size, 'white')
    draw = ImageDraw.Draw(img)
    
    try:
        # Try to use a default font, fall back to built-in if not available
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()
    except:
        # Use built-in font
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Draw title
    title_bbox = draw.textbbox((0, 0), title, font=font_large)
    title_width = title_bbox[2] - title_bbox[0]
    draw.text(((size[0] - title_width) // 2, 50), title, fill='black', font=font_large)
    
    # Draw fields
    y_offset = 120
    for field_name, field_value in fields.items():
        text = f"{field_name}: {field_value}"
        draw.text((50, y_offset), text, fill='black', font=font_small)
        y_offset += 40
    
    # Add a simple border
    draw.rectangle([10, 10, size[0]-10, size[1]-10], outline='black', width=2)
    
    return img

# Create test documents
documents = {
    'aadhaar_sample.jpg': {
        'title': 'AADHAAR CARD',
        'fields': {
            'Name': 'RAJESH KUMAR SHARMA',
            'DOB': '15/08/1990',
            'Gender': 'Male',
            'Address': '123 Gandhi Nagar, New Delhi 110001',
            'Aadhaar Number': '1234-5678-9012',
            'Phone': '+91 9876543210'
        }
    },
    'pan_sample.jpg': {
        'title': 'PERMANENT ACCOUNT NUMBER CARD',
        'fields': {
            'Name': 'RAJESH KUMAR SHARMA', 
            'Father Name': 'SURESH KUMAR SHARMA',
            'DOB': '15/08/1990',
            'PAN': 'ABCDE1234F',
            'Signature': '[Signature]'
        }
    },
    'passport_sample.jpg': {
        'title': 'PASSPORT',
        'fields': {
            'Passport No': 'Z1234567',
            'Name': 'RAJESH KUMAR SHARMA',
            'Nationality': 'INDIAN',
            'DOB': '15/08/1990',
            'Place of Birth': 'NEW DELHI',
            'Date of Issue': '10/01/2020',
            'Date of Expiry': '09/01/2030'
        }
    },
    'driving_license_sample.jpg': {
        'title': 'DRIVING LICENCE',
        'fields': {
            'DL No': 'DL0120201234567',
            'Name': 'RAJESH KUMAR SHARMA',
            'S/D/W of': 'SURESH KUMAR SHARMA', 
            'DOB': '15/08/1990',
            'Address': '123 Gandhi Nagar, New Delhi',
            'Date of Issue': '10/05/2018',
            'Valid Till': '09/05/2038',
            'Vehicle Class': 'LMV'
        }
    },
    'voter_id_sample.jpg': {
        'title': 'ELECTION PHOTO IDENTITY CARD',
        'fields': {
            'EPIC No': 'ABC1234567',
            'Name': 'RAJESH KUMAR SHARMA',
            'Father Name': 'SURESH KUMAR SHARMA',
            'Sex': 'M',
            'DOB': '15/08/1990',
            'Address': '123 Gandhi Nagar, New Delhi 110001'
        }
    },
    'birth_certificate_sample.jpg': {
        'title': 'BIRTH CERTIFICATE',
        'fields': {
            'Registration No': 'BC/2024/001234',
            'Name': 'RAJESH KUMAR SHARMA',
            'Date of Birth': '15/08/1990',
            'Place of Birth': 'New Delhi',
            'Father Name': 'SURESH KUMAR SHARMA',
            'Mother Name': 'SUNITA SHARMA',
            'Registrar': 'Deputy Registrar'
        }
    },
    'marksheet_10_sample.jpg': {
        'title': 'CLASS X MARK SHEET',
        'fields': {
            'Roll No': '1234567',
            'Name': 'RAJESH KUMAR SHARMA',
            'Father Name': 'SURESH KUMAR SHARMA',
            'DOB': '15/08/1990',
            'Year of Passing': '2006',
            'School': 'Delhi Public School',
            'Mathematics': '85',
            'Science': '88',
            'English': '82',
            'Hindi': '90',
            'Social Science': '87',
            'Total': '432/500',
            'Result': 'PASS'
        }
    },
    'marksheet_12_sample.jpg': {
        'title': 'CLASS XII MARK SHEET',
        'fields': {
            'Roll No': '7654321',
            'Name': 'RAJESH KUMAR SHARMA',
            'Father Name': 'SURESH KUMAR SHARMA',
            'DOB': '15/08/1990',
            'Year of Passing': '2008',
            'School': 'Delhi Public School',
            'Stream': 'Science (PCM)',
            'Physics': '88',
            'Chemistry': '85',
            'Mathematics': '92',
            'English': '80',
            'Physical Education': '95',
            'Total': '440/500',
            'Percentage': '88%',
            'Result': 'PASS'
        }
    }
}

# Create assets/test_docs directory if it doesn't exist
os.makedirs('assets/test_docs', exist_ok=True)

print("Creating sample test documents...")

for filename, doc_data in documents.items():
    filepath = os.path.join('assets', 'test_docs', filename)
    
    # Create the document image
    img = create_sample_document(
        filename, 
        doc_data['title'], 
        doc_data['fields'],
        size=(900, 700)
    )
    
    # Save the image
    img.save(filepath, 'JPEG', quality=95)
    print(f"✅ Created: {filepath}")

print(f"\n🎉 Successfully created {len(documents)} sample test documents!")
print(f"📁 Location: assets/test_docs/")
print(f"\n📄 Available documents:")
for filename in documents.keys():
    print(f"   - {filename}")