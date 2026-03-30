import ee

# Nashik ROI bounding box
ROI = [73.75, 19.95, 73.85, 20.05]


def init_gee():
    try:
        ee.Initialize(project="intrepid-vista-433114-m4")
    except:
        ee.Authenticate()
        ee.Initialize(project="intrepid-vista-433114-m4")
