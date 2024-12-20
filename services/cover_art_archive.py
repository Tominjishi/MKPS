import requests

def getReleaseGroupFrontCoverData(mbid, thumbnailSize=''):
    thumbnailPixels = {'s': '-250', 'm': '-500', 'l': '-1200'}
    
    url = f"https://coverartarchive.org/release-group/{mbid}/front{thumbnailPixels.get(thumbnailSize,'')}"
    try:
        response = requests.get(url)

        statusCodeMapping = {
            200: response.content,
            404: 'No Image',
            400: 'Invalid MBID'
        }
        
        statusCode = response.status_code
        returnContent = statusCodeMapping.get(statusCode, f"Error {statusCode}")
        return (statusCode, returnContent)
    except requests.RequestException as e:
        print(e)