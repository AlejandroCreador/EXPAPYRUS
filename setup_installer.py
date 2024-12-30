import PyInstaller.__main__
import os
from PIL import Image, ImageDraw, ImageFont

def create_expapyrus_icon():
    if not os.path.exists("expapyrus_icon.ico"):
        # Icon settings
        size = 256
        background_color = (255, 255, 255)
        primary_color = (52, 152, 219)
        secondary_color = (41, 128, 185)
        accent_color = (46, 204, 113)

        # Create base image
        icon = Image.new('RGB', (size, size), background_color)
        draw = ImageDraw.Draw(icon)

        # Draw base paper shape
        paper_points = [
            (size * 0.2, size * 0.15),  # Top left
            (size * 0.8, size * 0.15),  # Top right
            (size * 0.8, size * 0.85),  # Bottom right
            (size * 0.2, size * 0.85),  # Bottom left
        ]
        draw.polygon(paper_points, fill=primary_color)

        # Draw text lines with digital effect
        line_spacing = size * 0.08
        start_y = size * 0.25
        for i in range(6):
            # Vary line length for visual effect
            line_length = size * (0.5 - 0.05 * (i % 2))
            start_x = size * 0.3
            segments = 8
            segment_length = line_length / segments

            # Create segmented lines for digital effect
            for j in range(segments):
                x1 = start_x + (j * segment_length)
                x2 = x1 + segment_length * 0.8
                
                # Alternate colors for visual interest
                if j % 2 == 0:
                    color = secondary_color
                else:
                    color = accent_color

                draw.rectangle(
                    [x1, start_y + i * line_spacing,
                     x2, start_y + i * line_spacing + size * 0.02],
                    fill=color
                )

        # Add "E" symbol
        try:
            # Try to use Arial font
            font = ImageFont.truetype("arial.ttf", size=int(size * 0.2))
        except:
            # Fallback to default font if Arial is not available
            font = ImageFont.load_default()

        symbol_text = "E"
        # Calculate text dimensions for centering
        text_bbox = draw.textbbox((0, 0), symbol_text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        # Center the symbol
        symbol_position = (
            size * 0.25 - text_width / 2,
            size * 0.25 - text_height / 2
        )
        
        # Draw the symbol in white
        draw.text(
            symbol_position,
            symbol_text,
            font=font,
            fill=(255, 255, 255)
        )

        # Save multiple sizes for better compatibility
        sizes = [16, 32, 48, 64, 128, 256]
        icons = []
        
        # Create resized versions for each required size
        for icon_size in sizes:
            resized = icon.resize((icon_size, icon_size), Image.Resampling.LANCZOS)
            icons.append(resized)

        # Save as ICO file with all sizes included
        icons[0].save(
            "expapyrus_icon.ico",
            format='ICO',
            sizes=[(s, s) for s in sizes],
            append_images=icons[1:]
        )

def main():
    # Create the icon first
    create_expapyrus_icon()

    # Configure PyInstaller options
    PyInstaller.__main__.run([
        'expapyrus.py',                    # Main script
        '--name=Expapyrus',                # Output name
        '--onefile',                       # Create a single executable
        '--windowed',                      # GUI mode (no console)
        '--icon=expapyrus_icon.ico',       # Application icon
        '--add-data=expapyrus_icon.ico;.', # Include icon file
        '--clean',                         # Clean cache
        '--noconfirm',                     # Overwrite output
        # Required imports
        '--hidden-import=PIL',             # Pillow library
        '--hidden-import=pytesseract',     # OCR engine interface
        '--hidden-import=pdf2image',       # PDF conversion
        '--hidden-import=tkinter',         # GUI framework
    ])

if __name__ == "__main__":
    main()