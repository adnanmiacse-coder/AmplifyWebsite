from manim import *

config.background_color = BLACK

class Scene(MovingCameraScene):
    def construct(self):
        title = Text("Mitosis: The Stages", font_size=48)
        self.play(Write(title))
        self.wait(1)
        self.play(FadeOut(title))

        prophase_text = Text("Prophase: Chromosomes condense", font_size=30)
        self.play(Write(prophase_text))
        self.wait(1)
        self.play(FadeOut(prophase_text))

        metaphase_text = Text("Metaphase: Chromosomes align", font_size=30)
        self.play(Write(metaphase_text))
        self.wait(1)
        self.play(FadeOut(metaphase_text))

        anaphase_text = Text("Anaphase: Sister chromatids separate", font_size=30)
        self.play(Write(anaphase_text))
        self.wait(1)
        self.play(FadeOut(anaphase_text))

        telophase_text = Text("Telophase: New nuclei form", font_size=30)
        self.play(Write(telophase_text))
        self.wait(1)
        self.play(FadeOut(telophase_text))

        cytokinesis_text = Text("Cytokinesis: Cell divides", font_size=30)
        self.play(Write(cytokinesis_text))
        self.wait(2)
        self.play(FadeOut(cytokinesis_text))

        self.wait(2)