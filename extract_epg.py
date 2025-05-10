import gzip

# Input and output file paths
INPUT_FILE = "public/epg.xml.gz"
OUTPUT_FILE = "public/epg.xml"

def extract_gz():
    """
    Extract the compressed EPG XML file and save it as epg.xml.
    """
    try:
        with gzip.open(INPUT_FILE, 'rt', encoding='utf-8') as f_in, open(OUTPUT_FILE, 'w', encoding='utf-8') as f_out:
            f_out.write(f_in.read())
        print(f"Extracted EPG file created: {OUTPUT_FILE}")

    except FileNotFoundError:
        print(f"Error: The file {INPUT_FILE} was not found.")
    except Exception as e:
        print(f"Error during extraction: {e}")

if __name__ == "__main__":
    extract_gz()
