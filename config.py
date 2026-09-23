from pydantic import BaseModel, Field


class Config(BaseModel):
    window_width: int = Field(default=1024, ge=640, le=5000)
    window_height: int = Field(default=768, ge=480, le=5000)

    tile_size: int = Field(default=64, ge=8, le=512)

    fps: int = Field(default=60, ge=30, le=240)

    speed: int = Field(default=300, gt=299)

    font_path: str = Field(default="fonts/BlackOpsOne-Regular.ttf")

    gui_font_size: int = Field(default=24, gt=0, le=200)
    gui_text_color: str = Field(default="#ffffff")

    bg_color: str = Field(default="#006699")

    def parse_cli(self, **overrides) -> Config:
        updates = {k: v for k, v in overrides.items() if v is not None}
        current_data = self.model_dump()
        current_data.update(updates)
        return Config(**current_data)


CONFIG = Config()
