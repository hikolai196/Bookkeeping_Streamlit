import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image
from funct import load_image, resize_image, label_corners, deskew_image, image_to_bytes

def run_app():
    st.set_page_config(page_title="Image Deskewer", layout="wide")
    st.title("🖼️ Image Deskewer")
    st.write("Select four points as corners for the area to deskew.")

    st.sidebar.header("1. Upload Image")
    img_file = st.sidebar.file_uploader("Choose a PNG or JPG image", type=["png", "jpg", "jpeg"])

    st.sidebar.header("2. Select Corners")
    
    st.sidebar.header("3. Output Format")
    output_format = st.sidebar.radio("Choose output format", ["PNG", "JPG"])

    col1, col2 = st.columns(2)
    if img_file:
        try:
            image, img_np = load_image(img_file)
            resized_img, scale = resize_image(img_np)
            st.write("**Select four points (in order: top-left, top-right, bottom-right, bottom-left).**")
            st.write("Click on the image to add points. Drag to adjust.")

            canvas_result = st_canvas(
                fill_color="rgba(255, 0, 0, 0.3)",
                stroke_width=3,
                background_image=Image.fromarray(resized_img),
                update_streamlit=True,
                height=resized_img.shape[0],
                width=resized_img.shape[1],
                drawing_mode="point",
                point_display_radius=7,
                key="canvas"
            )

            points = []
            if canvas_result.json_data and "objects" in canvas_result.json_data:
                for obj in canvas_result.json_data["objects"]:
                    if obj["type"] == "circle":
                        # The center is at (left + radius, top + radius)
                        x = obj["left"] + obj["radius"]
                        y = obj["top"] + obj["radius"]
                        points.append([x, y])

            if len(points) == 4:
                orig_points = label_corners(points, scale)
                result_img = deskew_image(img_np, orig_points)
                st.success("Deskewed image generated below.")
                st.image(result_img, caption="Deskewed Output", use_container_width=True)
                img_bytes = image_to_bytes(result_img, output_format)
                ext = "png" if output_format == "PNG" else "jpg"
                st.download_button(
                    label=f"Download as {output_format}",
                    data=img_bytes,
                    file_name=f"deskewed.{ext}",
                    mime=f"image/{ext}"
                )
            elif len(points) > 4:
                st.error("You selected more than 4 points. Please clear and select exactly 4.")
            else:
                st.info("Select exactly 4 points to deskew.")

        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.info("Upload a PNG or JPG image to get started.")

    st.caption("Works on desktop and mobile. For best results, use a stylus or your finger on mobile.")
    st.markdown("""
    **Tips:**
    - If you make a mistake, use the canvas eraser or reload the image.
    - Points must be selected in order: top-left, top-right, bottom-right, bottom-left.
    - Large images are auto-resized for easier selection.
    """)