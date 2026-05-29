from manim import *

config.background_color = BLACK

class Scene(MovingCameraScene):
    def construct(self):
        title = Text("Mitosis: Cell Division", font_size=48)
        self.play(Write(title))
        self.wait(1)
        self.play(title.to_edge, UP)

        cell = Circle(radius=1, color=WHITE)
        cell_text = Text("Parent Cell", font_size=24).next_to(cell, DOWN)
        cell_group = VGroup(cell, cell_text)
        self.play(FadeIn(cell_group))
        self.wait(1)

        chromosome1 = Dot(point=cell.get_center() + LEFT*0.2 + UP*0.2, radius=0.1, color=RED)
        chromosome2 = Dot(point=cell.get_center() + RIGHT*0.2 + UP*0.2, radius=0.1, color=BLUE)
        chromosome3 = Dot(point=cell.get_center() + LEFT*0.2 + DOWN*0.2, radius=0.1, color=BLUE)
        chromosome4 = Dot(point=cell.get_center() + RIGHT*0.2 + DOWN*0.2, radius=0.1, color=RED)
        chromosomes = VGroup(chromosome1, chromosome2, chromosome3, chromosome4)

        self.play(FadeIn(chromosomes))
        self.wait(1)

        duplicated_chromosome1a = Dot(point=cell.get_center() + LEFT*0.4 + UP*0.4, radius=0.1, color=RED)
        duplicated_chromosome1b = Dot(point=cell.get_center() + LEFT*0.2 + UP*0.6, radius=0.1, color=RED)
        duplicated_chromosome2a = Dot(point=cell.get_center() + RIGHT*0.4 + UP*0.4, radius=0.1, color=BLUE)
        duplicated_chromosome2b = Dot(point=cell.get_center() + RIGHT*0.2 + UP*0.6, radius=0.1, color=BLUE)
        duplicated_chromosome3a = Dot(point=cell.get_center() + LEFT*0.4 + DOWN*0.4, radius=0.1, color=BLUE)
        duplicated_chromosome3b = Dot(point=cell.get_center() + LEFT*0.2 + DOWN*0.6, radius=0.1, color=BLUE)
        duplicated_chromosome4a = Dot(point=cell.get_center() + RIGHT*0.4 + DOWN*0.4, radius=0.1, color=RED)
        duplicated_chromosome4b = Dot(point=cell.get_center() + RIGHT*0.2 + DOWN*0.6, radius=0.1, color=RED)
        duplicated_chromosomes = VGroup(duplicated_chromosome1a, duplicated_chromosome1b,
                                        duplicated_chromosome2a, duplicated_chromosome2b,
                                        duplicated_chromosome3a, duplicated_chromosome3b,
                                        duplicated_chromosome4a, duplicated_chromosome4b)

        self.play(FadeOut(chromosomes), FadeIn(duplicated_chromosomes))
        self.wait(1)

        split_line = Line(cell.get_center() + LEFT*0.7, cell.get_center() + RIGHT*0.7, color=WHITE)
        self.play(Create(split_line))
        self.wait(1)

        daughter_cell1 = Circle(radius=1, color=WHITE).shift(LEFT*1.5)
        daughter_cell1s_text = Text("Daughter Cell 1", font_size=24).next_to(daughter_cell1, DOWN)
        daughter_cell2 = Circle(radius=1, color=WHITE).shift(RIGHT*1.5)
        daughter_cell2s_text = Text("Daughter Cell 2", font_size=24).next_to(daughter_cell2, DOWN)
        
        cell_group_clone = cell_group.copy()
        daughter_cell1.add(cell_group_clone)
        cell_group_clone2 = cell_group.copy()
        daughter_cell2.add(cell_group_clone2)

        self.play(self.camera.frame.animate.scale(0.7), FadeOut(cell_group), FadeOut(duplicated_chromosomes), FadeOut(split_line))
        self.play(
            FadeIn(daughter_cell1), FadeIn(daughter_cell1s_text),
            FadeIn(daughter_cell2), FadeIn(daughter_cell2s_text)
        )
        self.wait(2)