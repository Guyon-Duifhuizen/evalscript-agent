import json
import os

from openai import OpenAI
from sentinelhub import SHConfig
from sh_catalog import get_features
from sh_collections import list_byoc_collections


def convert_to_text(collection, gdf):
    collection_text = json.dumps(collection, indent=2)
    gdf_text = gdf.to_string()
    return collection_text, gdf_text


def generate_evalscript(query, collection_text, gdf_text):
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    prompt = (
        f"Create a {query} in plain JavaScript based on the following collection and"
        " geodataframe. Ensure that 'dataMask' is always included as an input band and"
        " the output band has four bands, with the last band being 'dataMask'. The"
        " evalscript should start with '//VERSION=3'. If the script involves"
        " calculating an index, consider using a color ramp and existing functions"
        " like 'ColorRampVisualizer' to enhance visualization. You can also make use"
        " of utility functions and visualizers for specific visualizations. For"
        " example, 'ColorMapVisualizer' and 'ColorRampVisualizer' can be used to map"
        " values to colors. Here are some examples:\n- ColorMapVisualizer: Sets the"
        " color from a discrete color map.\n  Example: const visualizer = new"
        " ColorMapVisualizer([[200, 0xff0000], [300, 0x0000ff]]);\n-"
        " ColorRampVisualizer: Maps values to colors using ramps.\n  Example: const"
        " visualizer = new ColorRampVisualizer([[200, 0xFF0000], [300,"
        " 0x0000FF]]);\nReturn the JavaScript code enclosed within ```javascript```"
        " markers. This ensures the code can be easily extracted. Note: If the"
        " collection is 'PlanetScope', it means the values are scaled with"
        f" 10000.\n\nCollection:\n{collection_text}\n\nGeoDataFrame:\n{gdf_text}"
    )

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="gpt-4o",
    )

    # Extract the JavaScript code between the ```javascript``` markers
    evalscript = chat_completion.choices[0].message.content
    start_marker = "```javascript\n"
    end_marker = "\n```"
    start_index = evalscript.find(start_marker) + len(start_marker)
    end_index = evalscript.find(end_marker, start_index)

    return evalscript[start_index:end_index].strip()


if __name__ == "__main__":
    config = SHConfig()
    collections = [
        c for c in list_byoc_collections(config) if "PlanetScope" in c["title"]
    ]
    collection = collections[0]
    gdf = get_features(config, collection["id"])
    gdf = gdf.to_crs(gdf.estimate_utm_crs().srs)

    # Convert collection and gdf to text
    collection_text, gdf_text = convert_to_text(collection, gdf)

    # Generate visual evalscript using ChatGPT
    visual_evalscript = generate_evalscript(
        "I would like to visualise NDWI from red to green", collection_text, gdf_text
    )
    print(visual_evalscript)
