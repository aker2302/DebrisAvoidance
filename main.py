from sgp4.api import Satrec, jday
from datetime import datetime, timedelta
from czml3.core import Document, Packet, Preamble
from czml3.properties import Position, Path, SolidColorMaterial,Label


# # URL for space debris TLE data on Celestrak
# debris_tle_url = "https://celestrak.org/NORAD/elements/gp.php?GROUP=cosmos-1408-debris&FORMAT=tle"#"https://celestrak.com/NORAD/elements/debris.txt"

# # Fetch the TLE data from Celestrak
# response = requests.get(debris_tle_url)
# tle_data = response.text



# Parse the TLE data
# Read the TLE data from a file
with open('debris.txt', 'r') as file:
    tle_data = file.read()

lines = tle_data.strip().split('\n')
tle_entries = [(lines[i], lines[i+1], lines[i+2]) for i in range(0, len(lines), 3)]

# Define start and end dates for propagation
start_date = datetime(2024, 7, 21)
end_date = datetime(2024, 8, 21)
step_minutes = 10

# Function to propagate TLE entries
def propagate_tle(entry, start_date, end_date, step_minutes):
    satellite = Satrec.twoline2rv(entry[1], entry[2])
    current_date = start_date
    steps = []
    while current_date <= end_date:
        steps.append(current_date)
        current_date += timedelta(minutes=step_minutes)

    data = []
    for date in steps:
        jd, fr = jday(date.year, date.month, date.day, date.hour, date.minute, date.second)
        e, r, v = satellite.sgp4(jd, fr)
        if e == 0:
            data.append([date, r])
    
    return data

# Debris trajectory positions
trajectory_pos = {}
for i in range(len(tle_entries)) :
    trajectory_pos[f"Cosmos 1408 DEB {i}"] = propagate_tle(tle_entries[i], start_date, end_date, step_minutes)

##################################################################################################################
##################################################################################################################
##################################################################################################################
##################################################################################################################
##################################################################################################################


# Czml creation


# Create CZML document
#czml_doc = Document()
czml_doc = []

# # Add a preamble packet
preamble = Preamble(
    name="COSMOS 1408 Debris Propagation",
    version="1.0",
)
czml_doc.append(preamble)

iter = 0

for debris in list(trajectory_pos.keys()) :

    # Convert positions to a format suitable for Cesium
    czml_positions = []
    leadTime = []
    trailTime = []

    data = trajectory_pos[debris]
    timesec = 0
    for i in range(len(data)-1):
        interval = (data[i][0]).strftime("%Y-%m-%dT%H:%M:%SZ")+"/"+(data[i+1][0]).strftime("%Y-%m-%dT%H:%M:%SZ")
        epoch = (data[i][0].strftime("%Y-%m-%dT%H:%M:%SZ"))
        numberlead = [0,step_minutes*60,step_minutes*60,0]
        numbertrail = [0,0,step_minutes*60,step_minutes*60]
        leadTime.append({"interval":interval,"epoch":epoch,"number":numberlead})
        trailTime.append({"interval":interval,"epoch":epoch,"number":numbertrail})
        czml_positions.append([timesec,data[i][1][0],data[i][1][1],data[i][1][2]])
        timesec += 600



    # for date, pos in data:
    #     timestamp = date.isoformat() + "Z"
    #     czml_positions.extend([timestamp, pos[0]*1000, pos[1]*1000, pos[2]*1000])  # Convert km to meters

    # Create the satellite packet
    debris_packet = Packet(
        id=debris,
        position=Position(
            interpolationAlgorithm="LAGRANGE",
            interpolationDegree=5,
            referenceFrame="INERTIAL",
            epoch=(data[0][0]).strftime("%Y-%m-%dT%H:%M:%SZ"),
            cartesian=czml_positions
        ),
        path=Path(
            show={"interval":(start_date).strftime("%Y-%m-%dT%H:%M:%SZ")+"/"+(end_date).strftime("%Y-%m-%dT%H:%M:%SZ"),"boolean":True},
            width=1,
            material={"solidColor": {"color": {"rgba": [255, 0, 0, 255]}}},
            leadTime=leadTime,
            trailTime=trailTime,
            resolution=120
        )
    )

    if iter < 1 :
        # Add packet to document
        czml_doc.append(debris_packet)
    iter += 1

CZML_file = Document(czml_doc)

# Write the CZML document to a file
with open('czml_files/czml_output.czml', 'w') as f:
    f.write(CZML_file.dumps(indent=2))

print("CZML file created: debris_trajectory.czml")


# # Example: Propagate the first TLE entry
# positions = propagate_tle(tle_entries[0], start_date, end_date, step_minutes)
# positions1 = propagate_tle(tle_entries[1], start_date, end_date, step_minutes)

# # Print positions
# for date, pos in positions:
#     print(f"Date: {date}, Position (km): {pos}")



