import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Cable Label Generator", layout="centered")
st.title("🏷️ Cable Label Generator")
st.write("Generate custom or automated label sheets instantly.")

# --- USER INPUT FORM ---
with st.form("label_form"):
    company = st.text_input("Company Name")
    project = st.text_input("Project Name")
    site = st.text_input("Site Name")
    cabinet = st.text_input("Cabinet Designation (e.g., Comms-A)")
    
    st.markdown("---")
    custom_format = st.text_input("Custom Naming Format (Optional)", 
                                  help="Leave blank to auto-generate. Use [NUM] where you want the count.")
    
    col1, col2 = st.columns(2)
    with col1:
        start_num = st.number_input("Outlet Start Number", min_value=0, value=1, step=1)
    with col2:
        end_num = st.number_input("Outlet End Number", min_value=1, value=24, step=1)
        
    export_format = st.selectbox("Export Software Target", ["Brother iLink/P-Touch", "Dymo Connect", "Standard CSV (Word/Excel)"])
    
    submit_button = st.form_submit_button(label="Generate Labels")

# --- APP LOGIC ---
if submit_button:
    if start_num > end_num:
        st.error("Error: Start number cannot be higher than end number.")
    else:
        labels_list = []
        
        # Loop through the numbers and pad with zeros (e.g., 01, 02)
        for i in range(int(start_num), int(end_num) + 1):
            num_str = f"{i:02d}" 
            
            # 1. Check if user provided a custom format string
            if custom_format:
                if "[NUM]" in custom_format:
                    label_text = custom_format.replace("[NUM]", num_str)
                else:
                    label_text = f"{custom_format}{num_str}"
            
            # 2. Automated fallback naming logic
            elif cabinet:
                label_text = f"{cabinet.upper()}-{num_str}"
            elif site:
                site_slug = "".join([word[0] for word in site.split()]).upper()
                label_text = f"{site_slug}-{num_str}"
            elif project:
                proj_slug = project.replace(" ", "-").upper()
                label_text = f"{proj_slug}-{num_str}"
            else:
                label_text = f"DATA-{num_str}" # Complete fallback
                
            labels_list.append(label_text)
        
        # Format the DataFrame based on what printer software requires
        if export_format == "Brother iLink/P-Touch":
            # Brother prefers a single column with a header name like "Text"
            df = pd.DataFrame({"Text": labels_list})
        elif export_format == "Dymo Connect":
            # Dymo easily maps to a column named "LabelText"
            df = pd.DataFrame({"LabelText": labels_list})
        else:
            # Word / Generic Mail Merge allows metadata columns
            df = pd.DataFrame({
                "Label": labels_list,
                "Company": [company] * len(labels_list),
                "Project": [project] * len(labels_list)
            })
            
        # Convert DataFrame to CSV in memory so it can be downloaded on a phone
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        csv_data = csv_buffer.getvalue()
        
        st.success(f"Successfully generated {len(labels_list)} labels!")
        
        # Mobile-friendly download button
        st.download_button(
            label=f"📥 Download CSV for {export_format}",
            data=csv_data,
            file_name=f"labels_{export_format.lower().replace(' ', '_')}.csv",
            mime="text/csv",
        )
