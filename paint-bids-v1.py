# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
import sys
import platform

# Check Python version compatibility
if sys.version_info < (3, 8):
    st.error("This application requires Python 3.8 or higher. Current version: " + platform.python_version())
    sys.exit(1)

# Streamlit app configuration
st.set_page_config(page_title="Residential Painting Bid Tool", page_icon="🎨")
st.title("Residential Painting Bid Tool - Mankato, MN (56001)")
st.markdown("Generate a professional painting bid for a residential job to be completed in one week.")

# Input form
st.header("Project Details")
sq_ft = st.number_input("House Square Footage (1,000–4,000 sq ft)", min_value=1000, max_value=4000, value=2000, step=100)
scope = st.selectbox("Painting Scope", ["Interior Only", "Exterior Only", "Both Interior and Exterior"])
prep_level = st.selectbox("Prep Work Complexity", ["Low (minimal prep)", "Medium (some scraping/patching)", "High (extensive prep)"])
crew_size = st.slider("Crew Size (number of painters)", min_value=1, max_value=4, value=2)

# Constants based on prior data
PAINTER_WAGE = 20  # Average of $18–$22/hour in MN 56001
PAINT_COST_PER_GALLON = 40  # Average cost of quality paint
GALLONS_PER_100_SQFT = 0.025  # 1 gallon covers ~400 sq ft, 2 coats
SUPPLIES_COST_PER_1000_SQFT = 50  # Brushes, tape, drop cloths, etc.
MARKUP_PERCENT = 0.45  # 20% profit + 25% overhead
MAX_WEEK_HOURS = 50  # Max hours a crew can work in one week (5 days x 10 hours/day)

# Time estimates (hours per 1,000 sq ft, adjusted for prep and scope)
TIME_ESTIMATES = {
    "Interior Only": {"Low": 10, "Medium": 12, "High": 15},
    "Exterior Only": {"Low": 12, "Medium": 15, "High": 20},
    "Both Interior and Exterior": {"Low": 22, "Medium": 27, "High": 35}
}

# Function to calculate hours
def calculate_hours(sq_ft, scope, prep_level):
    try:
        base_hours_per_1000 = TIME_ESTIMATES[scope][prep_level]
        total_hours = (sq_ft / 1000) * base_hours_per_1000
        return round(total_hours, 1)
    except KeyError as e:
        st.error(f"Error in hour calculation: Invalid scope or prep level ({e})")
        return 0

# Function to calculate costs
def calculate_costs(sq_ft, scope, prep_level, crew_size):
    try:
        # Labor hours
        total_hours = calculate_hours(sq_ft, scope, prep_level)
        hours_per_painter = total_hours / crew_size if crew_size > 0 else total_hours
        labor_cost = total_hours * PAINTER_WAGE

        # Material costs
        paint_area = sq_ft * 2 if scope == "Both Interior and Exterior" else sq_ft
        gallons_needed = (paint_area / 100) * GALLONS_PER_100_SQFT
        paint_cost = gallons_needed * PAINT_COST_PER_GALLON
        supplies_cost = (sq_ft / 1000) * SUPPLIES_COST_PER_1000_SQFT
        material_cost = paint_cost + supplies_cost

        # Total cost before markup
        subtotal = labor_cost + material_cost

        # Apply markup (overhead + profit)
        markup = subtotal * MARKUP_PERCENT
        total_cost = subtotal + markup

        return total_hours, hours_per_painter, labor_cost, material_cost, total_cost
    except Exception as e:
        st.error(f"Error in cost calculation: {e}")
        return 0, 0, 0, 0, 0

# Function to generate PDF bid
def generate_pdf_bid(sq_ft, scope, prep_level, crew_size, total_hours, labor_cost, material_cost, total_cost):
    try:
        filename = "painting_bid.pdf"
        c = canvas.Canvas(filename, pagesize=letter)
        c.setFont("Helvetica", 12)
        c.drawString(100, 750, "Painting Bid - Mankato, MN (56001)")
        c.drawString(100, 730, f"Date: {pd.Timestamp.now().strftime('%Y-%m-%d')}")
        c.drawString(100, 710, f"House Size: {sq_ft} sq ft")
        c.drawString(100, 690, f"Scope: {scope}")
        c.drawString(100, 670, f"Prep Work: {prep_level}")
        c.drawString(100, 650, f"Crew Size: {crew_size} painters")
        c.drawString(100, 630, f"Total Hours: {total_hours:.1f}")
        c.drawString(100, 610, f"Labor Cost: ${labor_cost:.2f}")
        c.drawString(100, 590, f"Material Cost: ${material_cost:.2f}")
        c.drawString(100, 570, f"Total Cost: ${total_cost:.2f}")
        c.drawString(100, 550, "Note: Bid assumes completion within one week.")
        c.save()
        return filename
    except Exception as e:
        st.error(f"Error generating PDF: {e}")
        return None

# Main logic: Generate and display bid
if st.button("Generate Bid"):
    # Calculate costs
    total_hours, hours_per_painter, labor_cost, material_cost, total_cost = calculate_costs(sq_ft, scope, prep_level, crew_size)
    
    if total_hours == 0:  # Check for calculation errors
        st.error("Calculation failed. Please check inputs and try again.")
    else:
        # Check if job can be completed in one week
        if hours_per_painter <= MAX_WEEK_HOURS:
            st.success(f"Job can be completed in one week with {crew_size} painters.")
            st.header("Bid Summary")
            st.write(f"**Total Hours**: {total_hours:.1f} hours")
            st.write(f"**Hours per Painter**: {hours_per_painter:.1f} hours")
            st.write(f"**Labor Cost**: ${labor_cost:.2f} (@ ${PAINTER_WAGE}/hour)")
            st.write(f"**Material Cost**: ${material_cost:.2f}")
            st.write(f"**Total Cost**: ${total_cost:.2f} (includes 45% markup for overhead/profit)")

            # Generate and offer PDF download
            pdf_file = generate_pdf_bid(sq_ft, scope, prep_level, crew_size, total_hours, labor_cost, material_cost, total_cost)
            if pdf_file:
                with open(pdf_file, "rb") as f:
                    st.download_button("Download Bid PDF", f, file_name=pdf_file, mime="application/pdf")
                os.remove(pdf_file)  # Clean up temporary file
        else:
            st.error(f"Job requires {hours_per_painter:.1f} hours per painter, exceeding the one-week limit of {MAX_WEEK_HOURS} hours. Increase crew size or reduce scope.")

# Footer
st.markdown("---")
st.markdown("Built with Streamlit for residential painting contractors in Mankato, MN. Assumes average wages and material costs for 56001.")
