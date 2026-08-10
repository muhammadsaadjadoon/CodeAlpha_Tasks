from io import BytesIO
from PIL import Image, ImageDraw
from app.services.image_preprocessing import preprocess_character

def test_preprocessing_returns_28x28_tensor():
    image=Image.new("RGB",(120,120),"white"); draw=ImageDraw.Draw(image); draw.line((35,15,35,100),fill="black",width=12); draw.line((35,55,85,55),fill="black",width=12)
    buf=BytesIO(); image.save(buf,"PNG")
    result=preprocess_character(buf.getvalue())
    assert result.tensor.shape==(1,1,28,28)
    assert 0 < result.foreground_ratio < 1
    assert result.preview_data_url.startswith("data:image/png;base64,")
