import streamlit as st

# Inject custom CSS
st.markdown("""
<style>
/* style.css */

/* Define CSS Variables for Colors (inspired by Shadcn UI defaults) */
:root {
    --background: #ffffff; /* Default background */
    --foreground: #020817; /* Default text color */
    --card: #ffffff; /* Card background */
    --card-foreground: #020817; /* Card text color */
    --popover: #ffffff; /* Popover background */
    --popover-foreground: #020817; /* Popover text color */
    --primary: #020817; /* Primary accent color (dark blue/black) */
    --primary-foreground: #f8f8f8; /* Text on primary */
    --secondary: #f1f5f9; /* Secondary accent color (light gray) */
    --secondary-foreground: #101010; /* Text on secondary */
    --muted: #f1f5f9; /* Muted background (for disabled, subtle elements) */
    --muted-foreground: #64748b; /* Muted text color */
    --accent: #f1f5f9; /* Accent background (for hover/active states) */
    --accent-foreground: #0f172a; /* Accent text color */
    --destructive: #ef4444; /* Destructive/error color */
    --destructive-foreground: #f8f8f8; /* Text on destructive */
    --border: #e2e8f0; /* Border color */
    --input: #e2e8f0; /* Input border color */
    --ring: #020817; /* Focus ring color */
    --radius: 0.5rem; /* Default border radius */

    /* Custom colors for alerts from your `alert.tsx` */
    --success: #22c55e;
    --success-background: #ecfdf5; /* Light green */
    --success-foreground: #065f46; /* Darker green text */

    --warning: #f59e0b;
    --warning-background: #fffbe6; /* Light yellow */
    --warning-foreground: #b45309; /* Darker yellow text */

    --info: #3b82f6;
    --info-background: #eff6ff; /* Light blue */
    --info-foreground: #1e40af; /* Darker blue text */

    /* For Streamlit's info/success/warning/error to match Shadcn's alert.tsx variants */
    /* You'll need to use specific color values for rgb to make rgba work. */
    --info-rgb: 59, 130, 246;
    --success-rgb: 34, 197, 94;
    --warning-rgb: 245, 158, 11;
    --destructive-rgb: 239, 68, 68; /* For error alerts */
}

/* Base styles for the app */
html, body {
    font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", "Noto Color Emoji";
    background-color: var(--background);
    color: var(--foreground);
}

/* Streamlit specific overrides */
.stApp {
    background-color: var(--background);
    color: var(--foreground);
}

/* Adjust main content padding */
.stApp > header {
    background-color: var(--background);
}

.st-emotion-cache-z5fcl4 { /* Target the main block container */
    padding-top: 2rem;
    padding-right: 2rem;
    padding-left: 2rem;
    padding-bottom: 2rem;
}

/* Remove default Streamlit component styling */
.stButton>button {
    border-radius: var(--radius);
    border: 1px solid var(--border);
    background-color: var(--background);
    color: var(--foreground);
    padding: 0.5rem 1rem;
    transition: all 0.2s ease-in-out;
}

.stButton>button:hover {
    background-color: var(--accent);
    color: var(--accent-foreground);
    border-color: var(--accent);
}

.stTextInput>div>div>input,
.stNumberInput>div>div>input,
.stSelectbox>div>div>div>div,
.stTextArea>div>div>textarea {
    border-radius: var(--radius);
    border: 1px solid var(--input);
    padding: 0.625rem 0.75rem;
    background-color: var(--background);
    color: var(--foreground);
    transition: border-color 0.2s, box-shadow 0.2s;
}

.stTextInput>div>div>input:focus,
.stNumberInput>div>div>input:focus,
.stSelectbox>div>div>div>div:focus,
.stTextArea>div>div>textarea:focus {
    border-color: var(--ring);
    box-shadow: 0 0 0 2px var(--ring);
    outline: none;
}

/* Custom styling for Streamlit's native elements to match Shadcn aesthetics */
.stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {
    color: var(--foreground);
    font-weight: 600; /* Semi-bold for titles */
    letter-spacing: -0.025em; /* Tighten letter spacing slightly */
}

.stMarkdown p {
    color: var(--foreground);
    line-height: 1.5;
}

.stAlert {
    border-radius: var(--radius);
    border: 1px solid var(--border);
    padding: 1rem 1.25rem;
    box-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.05); /* Subtle shadow */
}

/* Specific alert variants (adapting Streamlit's built-in alerts) */
.stAlert.info {
    border-color: rgba(var(--info-rgb), 0.5);
    background-color: var(--info-background);
    color: var(--info-foreground);
}
.stAlert.success {
    border-color: rgba(var(--success-rgb), 0.5);
    background-color: var(--success-background);
    color: var(--success-foreground);
}
.stAlert.warning {
    border-color: rgba(var(--warning-rgb), 0.5);
    background-color: var(--warning-background);
    color: var(--warning-foreground);
}
.stAlert.error { /* Streamlit's `st.error` typically uses red */
    border-color: rgba(var(--destructive-rgb), 0.5); /* Use destructive color */
    background-color: #fef2f2; /* Light red */
    color: #991b1b; /* Darker red text */
}

/* Adjust specific element padding and margins to match a compact, clean feel */
.st-emotion-cache-1cyp85t { /* Target text elements within Streamlit */
    margin-bottom: 0.5rem;
}

/* Specific styling for cards used with st.container */
.stCard {
    border-radius: var(--radius);
    border: 1px solid var(--border);
    background-color: var(--card);
    padding: 1.5rem;
    margin-bottom: 1rem;
    box-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1); /* subtle shadow */
}
.card-title {
    font-size: 1.5rem; /* text-2xl */
    font-weight: 600; /* font-semibold */
    margin-bottom: 0.5rem;
    color: var(--card-foreground);
    letter-spacing: -0.025em; /* tracking-tight */
}
.card-description {
    font-size: 0.875rem; /* text-sm */
    color: var(--muted-foreground);
    margin-bottom: 1rem;
}

/* More specific styling for text inputs */
.stTextInput label {
    font-weight: 500;
    margin-bottom: 0.5rem;
    display: block;
    color: var(--foreground);
    font-size: 0.875rem; /* text-sm */
}

/* Styling for secondary button variant */
.stButton>button[data-testid="stButton-secondary"] {
    background-color: var(--secondary);
    color: var(--secondary-foreground);
    border-color: var(--secondary);
}
.stButton>button[data-testid="stButton-secondary"]:hover {
    background-color: var(--secondary); /* Keep background solid on hover */
    filter: brightness(0.9); /* Slightly darken on hover */
}

/* Avatars CSS */
.stAvatar {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border-radius: 9999px; /* rounded-full */
    border: 1px solid var(--border);
    overflow: hidden;
    background-color: var(--muted);
    color: var(--muted-foreground);
    font-weight: 500;
    font-size: 1rem; /* Adjust as needed */
    width: 40px; /* h-10 w-10 (md size) */
    height: 40px;
    margin-right: 0.5rem;
    vertical-align: middle;
}
.stAvatar img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}
.stAvatarFallback {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
    height: 100%;
}

/* Badges CSS */
.stBadge {
    display: inline-flex;
    align-items: center;
    border-radius: 9999px; /* rounded-full */
    border: 1px solid var(--border);
    padding: 0.25rem 0.625rem; /* px-2.5 py-0.5 */
    font-size: 0.75rem; /* text-xs */
    font-weight: 600; /* font-semibold */
    transition: all 0.2s;
    margin-right: 0.5rem;
    margin-bottom: 0.5rem;
}
.stBadge.default {
    background-color: var(--primary);
    color: var(--primary-foreground);
    border-color: transparent;
}
.stBadge.secondary {
    background-color: var(--secondary);
    color: var(--secondary-foreground);
    border-color: transparent;
}
.stBadge.outline {
    background-color: transparent;
    color: var(--foreground);
    border-color: var(--border);
}
.stBadge.success-badge {
    background-color: rgba(var(--success-rgb), 0.2);
    color: var(--success-foreground);
    border-color: rgba(var(--success-rgb), 0.3);
}
</style>
""", unsafe_allow_html=True)

st.set_page_config(layout="centered", page_title="My Styled Streamlit App")

st.title("Welcome to My Styled Streamlit App")
st.write("This app demonstrates the integration of a modern UI aesthetic inspired by Shadcn UI components.")

# --- Example UI Elements ---

st.header("Cards (mimicking `card.tsx`)")
with st.container():
    st.markdown("<div class='stCard'>", unsafe_allow_html=True)
    st.markdown("<h3 class='card-title'>Card Title</h3>", unsafe_allow_html=True)
    st.markdown("<p class='card-description'>This is a beautiful card mimicking the Shadcn UI style.</p>", unsafe_allow_html=True)
    st.button("Card Button", key="card_button")
    st.markdown("</div>", unsafe_allow_html=True)


st.header("Buttons (mimicking `button.tsx`)")
st.button("Default Button")
st.button("Secondary Button", type="secondary")
# For outline, destructive, ghost, link, you would need more custom CSS for specific button styles
# based on their `key` or a new `data-testid` attribute if you want to target them more precisely.

st.header("Alerts (mimicking `alert.tsx`)")
st.info("This is an info alert.")
st.success("This is a success alert!")
st.warning("This is a warning.")
st.error("This is an error message.")

st.header("Input Fields (mimicking `form.tsx` and `input-otp.tsx` concepts)")
st.text_input("Your Name", placeholder="Enter your name...")
st.number_input("Your Age", min_value=0)

# For OTP input, you would typically need to create a custom component
# using st.components.v1.html or a combination of multiple st.text_input fields
# with strict length limits and custom styling for each slot.

st.header("Collapsible Sections (mimicking `collapsible.tsx` / `accordion.tsx`)")
with st.expander("Expand Me"):
    st.write("This content is now visible.")
    st.image("https://via.placeholder.com/150", caption="Placeholder Image")

st.header("Dropdowns (mimicking `dropdown-menu.tsx` / `context-menu.tsx`)")
# Streamlit's st.selectbox is the closest native component
selected_option = st.selectbox("Choose an Option", ["Option A", "Option B", "Option C"])
st.write(f"You selected: {selected_option}")

st.header("Avatars (mimicking `avatar.tsx`)")
st.markdown("""
<div style="display: flex; align-items: center; margin-bottom: 1rem;">
    <div class="stAvatar">
        <img src="https://avatars.githubusercontent.com/u/9906666?v=4" alt="User Avatar">
    </div>
    <p style="margin-bottom: 0;">User Profile</p>
</div>
<div style="display: flex; align-items: center;">
    <div class="stAvatar">
        <span class="stAvatarFallback">JD</span>
    </div>
    <p style="margin-bottom: 0;">John Doe</p>
</div>
""", unsafe_allow_html=True)


st.header("Badges (mimicking `badge.tsx`)")
st.markdown("<span class='stBadge default'>Default</span>", unsafe_allow_html=True)
st.markdown("<span class='stBadge secondary'>Secondary</span>", unsafe_allow_html=True)
st.markdown("<span class='stBadge outline'>Outline</span>", unsafe_allow_html=True)
st.markdown("<span class='stBadge success-badge'>Success</span>", unsafe_allow_html=True)


st.header("Dialogs/Drawers (mimicking `dialog.tsx`, `drawer.tsx`)")
# Streamlit's `st.popover` can be used to mimic some dialog/dropdown behavior for simpler cases.
# For full-screen or side drawers, you would typically need to use custom components (`st.components.v1.html`)
# or navigate to different pages/sections in a multi-page app structure.
with st.popover("Open Dialog"):
    st.markdown("<h3 class='card-title' style='font-size:1.25rem;'>Dialog Title</h3>", unsafe_allow_html=True)
    st.write("This is content inside a popover, behaving somewhat like a dialog.")
    st.button("Close Popover")

st.write("---")
st.write("Keep in mind that some complex components like `Carousel`, `Command Palette`, `Context Menu`, and advanced `Form` validations (beyond basic input fields) would require significant custom component development using `st.components.v1.html` to embed React/JavaScript code, or by utilizing existing Streamlit component libraries if their exact interactive behavior is crucial.")