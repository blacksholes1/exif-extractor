import os
import sys
import json
import subprocess
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def clean_path(path_input):
    """Cleans drag-and-drop formatting issues across platforms."""
    path = path_input.strip()
    if (path.startswith('"') and path.endswith('"')) or (path.startswith("'") and path.endswith("'")):
        path = path[1:-1]
    return path

def convert_to_degrees(value):
    """Helper function to convert the GPS coordinates stored in EXIF to degrees."""
    try:
        d = float(value[0])
        m = float(value[1])
        s = float(value[2])
        return d + (m / 60.0) + (s / 3600.0)
    except Exception:
        return None

def build_maps_link(gps_info):
    """Generates a clickable Google Maps link from extracted EXIF GPS tags."""
    lat_data = gps_info.get('GPSLatitude')
    lat_ref = gps_info.get('GPSLatitudeRef')
    lon_data = gps_info.get('GPSLongitude')
    lon_ref = gps_info.get('GPSLongitudeRef')
    
    if lat_data and lat_ref and lon_data and lon_ref:
        lat = convert_to_degrees(lat_data)
        lon = convert_to_degrees(lon_data)
        
        if lat is not None and lon is not None:
            if lat_ref != 'N': lat = -lat
            if lon_ref != 'E': lon = -lon
            return f"https://google.com{lat},{lon}"
    return None

def extract_image_metadata(file_path):
    """Extracts metadata from image files using Pillow."""
    data = {"SourceType": "Image", "Basic": {}, "EXIF": {}, "GPS": {}, "GoogleMapsLink": None}
    try:
        with Image.open(file_path) as img:
            data["Basic"]["Format"] = img.format
            data["Basic"]["Width"], data["Basic"]["Height"] = img.size
            data["Basic"]["Mode"] = img.mode

            exif_data = img.getexif()
            if exif_data:
                gps_raw_data = None
                for tag_id, value in exif_data.items():
                    tag_name = TAGS.get(tag_id, tag_id)
                    if tag_name == "GPSInfo":
                        gps_raw_data = value
                        continue
                    # Clean values for JSON serialization
                    data["EXIF"][str(tag_name)] = str(value)

                if gps_raw_data:
                    for gps_tag_id in gps_raw_data:
                        sub_tag_name = GPSTAGS.get(gps_tag_id, gps_tag_id)
                        val = gps_raw_data[gps_tag_id]
                        # Handle tuple/byte formats smoothly for human/JSON view
                        if isinstance(val, tuple):
                            val = [float(x) if hasattr(x, 'denominator') else str(x) for x in val]
                        elif isinstance(val, bytes):
                            val = val.decode(errors='ignore')
                        data["GPS"][str(sub_tag_name)] = val
                    
                    maps_link = build_maps_link(data["GPS"])
                    if maps_link:
                        data["GoogleMapsLink"] = maps_link
    except Exception as e:
        data["Error"] = f"Failed parsing image data: {str(e)}"
    return data

def extract_video_metadata(file_path):
    """Extracts metadata from video containers using FFmpeg/FFprobe."""
    data = {"SourceType": "Video", "Streams": [], "FormatMetadata": {}, "GoogleMapsLink": None}
    try:
        # Query ffprobe for json-formatted structural metadata
        command = [
            "ffprobe", "-v", "quiet", "-print_format", "json",
            "-show_format", "-show_streams", file_path
        ]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        probe_data = json.loads(result.stdout)
        
        data["FormatMetadata"] = probe_data.get("format", {}).get("tags", {})
        data["Streams"] = probe_data.get("streams", [])
        
        # Look for typical ISO/Apple video location strings (e.g. "+51.5074-0.1278/")
        location_string = probe_data.get("format", {}).get("tags", {}).get("location")
        if location_string:
            import re
            # Extract basic lat/long decimals from string markers
            match = re.match(r'([+-]\d+\.\d+)([+-]\d+\.\d+)', location_string)
            if match:
                lat, lon = match.group(1), match.group(2)
                data["GoogleMapsLink"] = f"https://google.com{lat},{lon}"
                
    except (subprocess.CalledProcessError, FileNotFoundError):
        data["Error"] = "FFmpeg/FFprobe utility is missing or failed on this machine."
    except Exception as e:
        data["Error"] = f"Failed parsing video data: {str(e)}"
    return data

def export_to_json(file_path, metadata):
    """Writes compiled dictionary data safely into a clean JSON layout file."""
    dir_name, file_name = os.path.split(file_path)
    base_name, _ = os.path.splitext(file_name)
    export_path = os.path.join(dir_name, f"{base_name}_metadata.json")
    
    try:
        with open(export_path, 'w', encoding='utf-8') as j_file:
            json.dump(metadata, j_file, indent=4, ensure_ascii=False)
        return export_path
    except Exception as e:
        print(f"❌ Failed to export JSON tracking sheet: {str(e)}")
        return None

def process_file(user_input):
    file_path = clean_path(user_input)
    if not os.path.exists(file_path):
        print(f"\n❌ Error: The file path '{file_path}' does not exist.")
        return

    _, file_name = os.path.split(file_path)
    _, ext = os.path.splitext(file_name)
    ext_lower = ext.lower()

    image_exts = ['.jpg', '.jpeg', '.png', '.webp', '.tiff', '.bmp']
    video_exts = ['.mp4', '.mkv', '.mov', '.avi', '.m4v']

    print("\n" + "="*60)
    print(f"🔍 SCANNING FILE: {file_name}")
    print("="*60)

    if ext_lower in image_exts:
        meta = extract_image_metadata(file_path)
    elif ext_lower in video_exts:
        meta = extract_video_metadata(file_path)
    else:
        print("❌ Unsupported extension target profile.")
        return

    # Error handling display
    if "Error" in meta:
        print(f"❌ {meta['Error']}")
        return

    # Display Core Visual Information to Terminal
    if meta["SourceType"] == "Image":
        print(f"📸 Image Resolution: {meta['Basic'].get('Width')}x{meta['Basic'].get('Height')} px")
        print(f"🔑 Key Tags Found:   {len(meta['EXIF'])} items listed.")
    else:
        print(f"🎬 Video Container:  {len(meta['Streams'])} track tracks detected.")
        if meta["FormatMetadata"]:
            print(f"🔑 Global Metadata: {len(meta['FormatMetadata'])} fields found.")

    # Location Output
    if meta.get("GoogleMapsLink"):
        print(f"\n🌍 GOOGLE MAPS GPS LINK IDENTIFIED:")
        print(f"🔗 {meta['GoogleMapsLink']}")
    else:
        print("\n🌍 GPS Location: None found in headers.")

    # Export Step
    json_target = export_to_json(file_path, meta)
    if json_target:
        print(f"\n💾 Metadata exported successfully to text archive!")
        print(f"📂 JSON File Location: {json_target}")
    print("="*60 + "\n")

def main():
    clear_screen()
    print("============================================================")
    print("          🌟 ADVANCED MEDIA METADATA SCANNER & EXPORTER    ")
    print("============================================================")
    
    while True:
        try:
            print("👇 Drag & drop your image or video file directly here")
            print("   (Or type 'exit' to quit)")
            user_input = input("\nFile Path: ")
            
            if user_input.strip().lower() == 'exit':
                print("Exiting tool. Data archived safely.")
                break
            if not user_input.strip():
                continue
                
            process_file(user_input)
            print("-" * 60)
        except KeyboardInterrupt:
            print("\nExiting tool.")
            sys.exit(0)

if __name__ == "__main__":
    main()
