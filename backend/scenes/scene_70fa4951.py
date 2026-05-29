from manim import *

config.background_color = BLACK

class Scene(MovingCameraScene):
    def construct(self):
        title = Text("Mitosis: Cell Division", font_size=40).to_edge(UP)
        self.play(Write(title))

        cell_circle = Circle(radius=1.5, color=WHITE)
        cell_nucleus = Circle(radius=0.5, color=YELLOW).move_to(cell_circle.get_center())
        cell_group = VGroup(cell_circle, cell_nucleus)
        self.play(Create(cell_group))
        self.wait(1)

        dna_text = MathTex("DNA", color=GREEN).scale(0.7).move_to(cell_nucleus.get_center())
        self.play(FadeIn(dna_text, shift=UP))
        self.wait(1)

        duplicated_dna = MathTex("2x DNA", color=GREEN).scale(0.7).move_to(cell_nucleus.get_center())
        self.play(Transform(dna_text, duplicated_dna))
        self.wait(1)

        nucleus_splits_left = cell_nucleus.copy().shift(LEFT*0.5)
        nucleus_splits_right = cell_nucleus.copy().shift(RIGHT*0.5)
        
        new_nucleus_group = VGroup(nucleus_splits_left, nucleus_splits_right)
        self.play(Transform(cell_nucleus, new_nucleus_group))
        self.wait(1)

        cell_membrane = Line(cell_circle.get_left(), cell_circle.get_right(), color=WHITE)
        cell_membrane.stretch(1.2, dim=1).move_to(cell_circle.get_center())
        self.play(Create(cell_membrane))
        self.wait(1)

        final_cell_left = Cell(radius=1.3, nucleus_radius=0.4).shift(LEFT*1.5)
        final_cell_right = Cell(radius=1.3, nucleus_radius=0.4).shift(RIGHT*1.5)
        
        final_cells_group = VGroup(final_cell_left, final_cell_right)

        self.play(Transform(cell_group, final_cells_group[0]))
        self.remove(cell_group)
        self.add(final_cells_group[0])
        
        self.play(Transform(final_cells_group[0], final_cells_group[1]))
        self.remove(final_cells_group[0])
        self.add(final_cells_group[1])


        self.wait(2)

class Cell(VGroup):
    def __init__(self, radius=1, color=WHITE, nucleus_radius=0.3, nucleus_color=YELLOW):
        super().__init__()
        outer_circle = Circle(radius=radius, color=color)
        inner_circle = Circle(radius=nucleus_radius, color=nucleus_color)
        inner_circle.move_to(outer_circle.get_center())
        self.add(outer_circle, inner_circle)