from manim import *

config.background_color = BLACK

class Scene(Scene):
    def construct(self):
        title = Text("Cell Structure and Division", font_size=48)
        self.play(Write(title))
        self.wait(1)
        self.play(FadeOut(title))

        cell_text = Text("Cell", font_size=36)
        nucleus_text = Text("Nucleus", font_size=30)
        dna_text = MathTex("DNA", font_size=36)

        cell = Circle(radius=1.5, color=WHITE)
        nucleus = Circle(radius=0.5, color=BLUE)
        nucleus.move_to(cell.get_center())
        
        cell_group = VGroup(cell, nucleus)
        
        self.play(Create(cell))
        self.play(cell.animate.scale(1.2))
        self.play(FadeIn(nucleus_text, shift=UP))
        nucleus.move_to(cell.get_center() + UP*0.8)
        self.play(FadeIn(dna_text, shift=DOWN))
        dna_text.next_to(nucleus, DOWN)
        self.play(Write(cell_text))
        cell_text.to_edge(UL)

        division_arrow = Arrow(start=cell.get_right() + RIGHT*0.5, end=cell.get_right() + RIGHT*2, buff=0.5)
        division_text = Text("Cell Division", font_size=36)
        division_text.next_to(division_arrow, RIGHT)

        self.play(GrowArrow(division_arrow))
        self.play(Write(division_text))
        self.wait(1)

        self.play(FadeOut(cell_group), FadeOut(dna_text), FadeOut(nucleus_text), FadeOut(division_arrow), FadeOut(division_text), FadeOut(cell_text))

        cancer_title = Text("Cancer: Uncontrolled Division", font_size=40)
        self.play(Write(cancer_title))
        self.wait(2)