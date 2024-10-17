import streamlit as st
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Conversion function from inches to millimeters
def inches_to_mm(inches):
    return round(inches * 25.4, 2)

# Function to create a PDF
def create_pdf(shades_data, total_yardage, customer):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Add customer name and mechanism type on each page
    for idx, shade in enumerate(shades_data):
        c.setFont("Helvetica", 10)
        block_height = height / 3
        for i in range(3):
            top_margin = height - i * block_height
            # Left Column - Inputs
            c.drawString(50, top_margin - 30, f"Customer: {customer}")
            c.drawString(50, top_margin - 50, f"Roller Shade #{idx + 1} - {shade['Room']}")
            c.drawString(50, top_margin - 70, f"Style and Color: {shade['Style and Color']}")
            c.drawString(50, top_margin - 90, f"Mechanism: {shade['Mechanism']}")
            c.drawString(50, top_margin - 110, f"Control Location: {shade['Input']['Control Location']}")
            c.drawString(50, top_margin - 130, f"Roll Orientation: {shade['Input']['Roll Orientation']}")
            c.drawString(50, top_margin - 150, f"Width: {shade['Input']['Width']} inches")
            c.drawString(50, top_margin - 170, f"Height: {shade['Input']['Height']} inches")
            c.drawString(50, top_margin - 190, f"Mount: {shade['Input']['Mount']}")
            c.drawString(50, top_margin - 210, f"Cassette: {shade['Output']['Cassette']}")
            c.drawString(50, top_margin - 230, f"Roll Width: {shade['Input']['Roll Width']} inches")

            # Right Column - Outputs
            c.drawString(300, top_margin - 50, f"Tube Width: {shade['Output']['Tube Width']} inches")
            c.drawString(300, top_margin - 70, f"Bottom Bar Width: {shade['Output']['Bottom Bar Width']} inches")
            c.drawString(300, top_margin - 90, f"Fabric Width: {shade['Output']['Fabric Width']} inches ({inches_to_mm(shade['Output']['Fabric Width'])} mm)")
            c.drawString(300, top_margin - 110, f"Fabric Height: {shade['Output']['Fabric Height']} inches ({inches_to_mm(shade['Output']['Fabric Height'])} mm)")
            c.drawString(300, top_margin - 130, f"Cassette Width: {shade['Output']['Cassette Width']} inches")
            c.drawString(300, top_margin - 150, f"Mechanism Type: {shade['Output']['Mechanism Type']}")
            c.drawString(300, top_margin - 170, f"Yardage: {shade['Output']['Yardage']} yards")

            c.line(50, top_margin - block_height + 10, width - 50, top_margin - block_height + 10)

        c.showPage()  # Add new page for each roller shade

    # Final page with total yardage
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, height - 100, f"Customer: {customer}")
    c.drawString(50, height - 130, f"Total Yardage for All Shades: {total_yardage} yards")
    c.showPage()
    c.save()

    buffer.seek(0)
    return buffer


# Function to convert fraction to decimal
def fraction_to_decimal(fraction):
    fractions = {
        '1/8"': 0.125,
        '1/4"': 0.25,
        '3/8"': 0.375,
        '1/2"': 0.5,
        '5/8"': 0.625,
        '3/4"': 0.75,
        '7/8"': 0.875,
        '0"': 0.0
    }
    return fractions[fraction]

# Function to perform calculations for each roller shade
def calculate_shade(width, height, mount, cassette, mechanism, control_location, roll_orientation, roll_width):
    fabric_width = width - 1.25  # Fabric Width Calculation
    if mount == "Outside Mount":
        fabric_height = height + 16
        cassette_width = width - 0.375 if cassette == "Yes" else "No"
    else:  # Inside Mount
        fabric_height = height + 16
        cassette_width = width - 0.625 if cassette == "Yes" else "No"

    # Set Tube Width and Bottom Bar Width same as Fabric Width
    tube_width = fabric_width
    bottom_bar_width = fabric_width

    # Mechanism logic with the new "Cordless" mechanism rules
    if mechanism == "Cordless":
        if width > 20 and width < 90:
            mechanism_type = "Medium Cordless Spring + Handle"
        elif width >= 90:
            mechanism_type = "Large Cordless Spring + Handle"
        else:
            mechanism_type = "Small Cordless Spring + Handle"
    elif mechanism in ["Motorized with remote", "Motorized with remote and hub", "Somfy Motorized With Remote", "Somfy Motorized With Remote And Hub"]:
        if width > 20 and width < 96:
            mechanism_type = "Regular Motor 1.1"
        elif width >= 96:
            mechanism_type = "Large Motor 2.0"
        else:
            mechanism_type = "Check if motor fits"
    else:
        mechanism_type = "Manual (Clutch)"

    # Yardage calculation
    yardage = fabric_height / 36
    yardage = round(yardage, 1)

    return {
        "Tube Width": tube_width,
        "Bottom Bar Width": bottom_bar_width,
        "Fabric Width": fabric_width,
        "Fabric Height": fabric_height,
        "Cassette Width": cassette_width,
        "Cassette": cassette,  # Display No if cassette is not selected
        "Mechanism Type": mechanism_type,
        "Yardage": yardage,
        "Control Location": control_location,  # Include control location in output
        "Roll Orientation": roll_orientation  # Include roll orientation in output
    }

# Initialize session state for roller shade data
if 'shades' not in st.session_state:
    st.session_state['shades'] = []

# Section 1: Select the number of roller shades and customer name
st.title("Roller Shade Production Work Order")
customer = st.text_input("Customer", max_chars=40)
num_shades = st.number_input("Select the number of Roller Shades", min_value=1, max_value=50, value=1)

# Section 2: Input variables for each roller shade
for i in range(num_shades):
    st.subheader(f"Roller Shade #{i + 1}")
    room = st.text_input(f"Room for Roller Shade #{i + 1}", max_chars=40)
    style_color = st.text_input(f"Style and Color for Roller Shade #{i + 1}", max_chars=40)
    mechanism = st.selectbox(f"Mechanism for Roller Shade #{i + 1}", [
        "Cordless", "Motorized with remote", "Motorized with remote and hub", 
        "Clutch left", "Clutch right", "Somfy Motorized With Remote", 
        "Somfy Motorized With Remote And Hub", "Lutron Motorized"
    ])
    control_location = st.selectbox(f"Control Location for Roller Shade #{i + 1}", ["Left", "Right"])
    roll_orientation = st.selectbox(f"Roll Orientation for Roller Shade #{i + 1}", ["Regular", "Reverse"])

    # Width and Height input with integer and fraction
    width_int = st.number_input(f"Roller Shade Width (inches) - Integer part for Roller Shade #{i + 1}", min_value=0, step=1, value=36)
    width_fraction = st.selectbox(f"Fraction for Roller Shade Width #{i + 1}", ['0"', '1/8"', '1/4"', '3/8"', '1/2"', '5/8"', '3/4"', '7/8"'])
    shade_width = width_int + fraction_to_decimal(width_fraction)
    
    height_int = st.number_input(f"Roller Shade Height (inches) - Integer part for Roller Shade #{i + 1}", min_value=0, step=1, value=64)
    height_fraction = st.selectbox(f"Fraction for Roller Shade Height #{i + 1}", ['0"', '1/8"', '1/4"', '3/8"', '1/2"', '5/8"', '3/4"', '7/8"'])
    shade_height = height_int + fraction_to_decimal(height_fraction)

    mount = st.selectbox(f"Mount for Roller Shade #{i + 1}", ["Inside Mount", "Outside Mount"])
    cassette = st.selectbox(f"Cassette for Roller Shade #{i + 1}", ["Yes", "No"])
    roll_width = st.number_input(f"Roll Width for Roller Shade #{i + 1}", min_value=0.0, value=118.0)

    if st.button(f"Calculate Roller Shade #{i + 1}"):
        output = calculate_shade(shade_width, shade_height, mount, cassette, mechanism, control_location, roll_orientation, roll_width)
        st.session_state['shades'].append({
            "Room": room,
            "Style and Color": style_color,
            "Mechanism": mechanism,
            "Input": {
                "Width": shade_width,
                "Height": shade_height,
                "Mount": mount,
                "Cassette": cassette,
                "Roll Width": roll_width,
                "Control Location": control_location,  # Include control location in input
                "Roll Orientation": roll_orientation  # Include roll orientation in input
            },
            "Output": output
        })

# Section 3: Display the outputs for each roller shade
if st.session_state['shades']:
    st.subheader("Output Variables")
    total_yardage = 0
    for idx, shade in enumerate(st.session_state['shades']):
        st.write(f"**Roller Shade #{idx + 1}**")
        st.write(f"Room: {shade['Room']}")
        st.write(f"Style and Color: {shade['Style and Color']}")
        st.write(f"Mechanism: {shade['Mechanism']}")
        st.write(f"Control Location: {shade['Input']['Control Location']}")
        st.write(f"Roll Orientation: {shade['Input']['Roll Orientation']}")
        st.write(f"Mechanism Type: {shade['Output']['Mechanism Type']}")
        st.write(f"Tube Width: {shade['Output']['Tube Width']} inches")
        st.write(f"Bottom Bar Width: {shade['Output']['Bottom Bar Width']} inches")
        st.write(f"Fabric Width: {shade['Output']['Fabric Width']} inches ({inches_to_mm(shade['Output']['Fabric Width'])} mm)")
        st.write(f"Fabric Height: {shade['Output']['Fabric Height']} inches ({inches_to_mm(shade['Output']['Fabric Height'])} mm)")
        st.write(f"Cassette: {shade['Output']['Cassette']}")
        st.write(f"Yardage: {shade['Output']['Yardage']}")
        total_yardage += shade['Output']['Yardage']
    
    st.subheader(f"Total Yardage for All Shades: {round(total_yardage, 1)} yards")

    # Button to download the PDF
    if st.button("Download PDF"):
        pdf_buffer = create_pdf(st.session_state['shades'], total_yardage, customer)
        st.download_button(
            label="Download Production Work Order as PDF",
            data=pdf_buffer,
            file_name="roller_shade_production_work_order.pdf",
            mime="application/pdf"
        )
