import streamlit as st
from helpers.config import AWSBedrockModelInfo, AWSBedrockModelDescription
from helpers.loog import logger

class HomePage:
    def __init__(self):
        self.models = sorted(
            [
                AWSBedrockModelInfo(
                    name=name,
                    description=data["description"],
                    tags=data["tags"],
                    logo=data["logo"],
                )
                for name, data in AWSBedrockModelDescription.DATA.items()
            ],
            key=lambda m: m.name.lower(),
        )

    def display(self):
        st.title("🚀 Yang - GenAI")

        st.markdown("### 🧠 AWS Bedrock Model")

        cols = st.columns(4)
        for i, model in enumerate[AWSBedrockModelInfo](self.models):
            col = cols[i % 4]
            with col:
                self.render_model_card(model)
    
    def render_model_card(self, model: AWSBedrockModelInfo):
        """Renders each tool in a card format with click behavior."""
        card_key = f"tool_{model.name}"

        with st.container():
            st.markdown(
            f"""
            <div style="
                border-radius: 12px;
                padding: 15px;
                margin: 8px 0;
                background-color: #f9f9f9;
                box-shadow: 0 1px 4px rgba(0,0,0,0.1);
                cursor: pointer;
                transition: 0.2s;
            "
                onmouseover="this.style.backgroundColor='#f0f0f0';"
                onmouseout="this.style.backgroundColor='#f9f9f9';"
            >
                <h4 style="margin-bottom:6px;">{model.logo} {model.name}</h4>
                <p style="font-size: 14px; margin-top: 0; color: #555;">{model.description}</p>
                <div style="display:flex; flex-wrap:wrap; gap:4px;">
                    {''.join([
                        f'<span style="background-color:#e0f2ff;color:#007bff;padding:2px 8px;border-radius:8px;font-size:12px;">{tag}</span>'
                        for tag in model.tags
                    ])}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        
    def run(self):
        self.display()

def main():
    try:
        page = HomePage()
        page.run()
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        st.error("An unexpected error occurred. Please refresh the page and try again.")
        st.exception(e)

if __name__ == "__main__":
    main()