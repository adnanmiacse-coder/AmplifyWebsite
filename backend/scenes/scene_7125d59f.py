from manim import *

config.background_color = BLACK

class Mitosis(MovingCameraScene):
    def construct(self):
        title = Text("Mitosis: Cell Division", font_size=36)
        self.play(Write(title))
        self.wait(1)
        self.play(FadeOut(title))

        cell = Circle(radius=1, color=WHITE)
        nucleus = Circle(radius=0.3, color=BLUE)
        cell.move_to(ORIGIN)
        nucleus.move_to(ORIGIN)
        cell_group = VGroup(cell, nucleus)

        self.play(Create(cell_group))
        self.wait(1)

        chromosomes = VGroup()
        for i in range(4):
            chr = Line(start=[-0.5 + i * 0.2, 0, 0], end=[-0.5 + i * 0.2, 0.2, 0], color=RED)
            chromosomes.add(chr)

        chr_copy = chromosomes.copy()
        chr_copy.shift(RIGHT * 0.5)
        chromosomes.shift(LEFT * 0.5)
        
        nucleus_content = VGroup(chromosomes, chr_copy)
        nucleus.add(nucleus_content)

        self.play(Create(chromosomes), Create(chr_copy))
        self.wait(1)

        self.play(self.camera.frame.animate.scale(0.8))
        self.play(self.camera.frame.animate.shift(UP*0.5))

        nucleus_split = nucleus.copy()
        nucleus_split.shift(UP*0.5)


        new_cell_1 = cell.copy()
        new_cell_1.shift(UP*0.5)
        new_cell_1.scale(0.7)


        new_cell_2 = cell.copy()
        new_cell_2.shift(DOWN*0.5)
        new_cell_2.scale(0.7)

        daughter_nucleus_1 = nucleus.copy()
        daughter_nucleus_1.shift(UP*0.5)
        daughter_nucleus_1.scale(0.5)

        daughter_nucleus_2 = nucleus.copy()
        daughter_nucleus_2.shift(DOWN*0.5)
        daughter_nucleus_2.scale(0.5)

        self.play(Transform(cell, VGroup(new_cell_1, new_cell_2)))
        self.play(FadeOut(nucleus_content))
        self.play(Transform(nucleus, VGroup(daughter_nucleus_1, daughter_nucleus_2)))


        self.wait(2)