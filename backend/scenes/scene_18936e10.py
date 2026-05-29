from manim import *
config.background_color = BLACK

class Scene(MovingCameraScene):
    def construct(self):
        # Title Card
        title = Text("Mitosis: The Cell Cycle", color=YELLOW).scale(1.5)
        self.play(Write(title))
        self.wait(3)
        self.play(FadeOut(title))
        self.wait(1.5)

        # Step 1: Introduction - A single cell
        cell_intro = Circle(radius=1.5, color=BLUE)
        cell_label = Text("Parent Cell", color=WHITE).next_to(cell_intro, DOWN)
        self.play(Create(cell_intro), Write(cell_label))
        self.wait(3)

        # Step 2: Chromosomes appear
        chromosomes_group = VGroup()
        chromosome1_in = Line(cell_intro.get_center() + UP*0.5, cell_intro.get_center() + DOWN*0.5, color=RED)
        chromosome2_in = Line(cell_intro.get_center() + LEFT*0.5, cell_intro.get_center() + RIGHT*0.5, color=RED)
        chromosomes_in_label = Text("Chromosomes", color=WHITE).next_to(chromosomes_group, DOWN)

        self.play(
            Create(chromosome1_in),
            Create(chromosome2_in),
            FadeOut(cell_label),
            cell_intro.animate.scale(0.8).to_edge(UP)
        )
        chromosomes_group.add(chromosome1_in, chromosome2_in)
        chromosomes_in_label.move_to(cell_intro.get_center() + DOWN * 0.7)
        self.play(Write(chromosomes_in_label))
        self.wait(3)

        # Step 3: Prophase - Chromosomes condense
        original_chromosomes = VGroup(chromosome1_in, chromosome2_in)
        condensed_chromosome1 = original_chromosomes[0].copy().scale(0.5).set_color(PURPLE)
        condensed_chromosome2 = original_chromosomes[1].copy().scale(0.5).set_color(PURPLE)
        condensed_chromosomes_group = VGroup(condensed_chromosome1, condensed_chromosome2)
        self.play(Transform(original_chromosomes, condensed_chromosomes_group))
        self.wait(3)

        # Step 4: Metaphase - Chromosomes align at the metaphase plate
        metaphase_plate = Line(LEFT*2, RIGHT*2, color=GREEN).shift(DOWN*1.5)
        metaphase_label = Text("Metaphase Plate", color=GREEN).next_to(metaphase_plate, DOWN)
        self.play(
            FadeOut(chromosomes_in_label),
            FadeOut(cell_intro),
            original_chromosomes.animate.arrange(RIGHT, buff=0.5).move_to(metaphase_plate.get_center() + UP*0.5)
        )
        self.play(Create(metaphase_plate), Write(metaphase_label))
        self.wait(3)

        # Step 5: Anaphase - Sister chromatids separate
        separating_arrow_left = Arrow(original_chromosomes[0].get_left(), LEFT*3, color=ORANGE)
        separating_arrow_right = Arrow(original_chromosomes[1].get_right(), RIGHT*3, color=ORANGE)
        separated_label = Text("Sister Chromatids Separate", color=ORANGE).next_to(separating_arrow_left, DOWN)

        self.play(
            GrowArrow(separating_arrow_left),
            GrowArrow(separating_arrow_right),
            Write(separated_label)
        )
        self.wait(3)
        self.play(
            original_chromosomes[0].animate.shift(LEFT*3),
            original_chromosomes[1].animate.shift(RIGHT*3),
            FadeOut(metaphase_plate),
            FadeOut(metaphase_label)
        )
        self.wait(3)

        # Step 6: Telophase & Cytokinesis - Two new cells form
        new_cell1 = Circle(radius=1.5, color=BLUE).shift(LEFT*3)
        new_cell2 = Circle(radius=1.5, color=BLUE).shift(RIGHT*3)
        new_cells_label = Text("Two Daughter Cells", color=BLUE).next_to(VGroup(new_cell1, new_cell2), DOWN)

        self.play(
            FadeOut(original_chromosomes),
            FadeOut(separating_arrow_left),
            FadeOut(separating_arrow_right),
            FadeOut(separated_label),
            Create(new_cell1),
            Create(new_cell2)
        )
        self.play(Write(new_cells_label))
        self.wait(3)

        # Summary
        summary_text = Text("Mitosis: One parent cell divides to produce two identical daughter cells.", color=WHITE)
        summary_text.scale(0.8).to_edge(DOWN)
        self.play(FadeOut(new_cells_label), original_chromosomes.animate.move_to(ORIGIN).scale(1.2).set_color(WHITE))
        self.play(Write(summary_text))
        self.wait(3)
        self.play(FadeOut(VGroup(*self.mobjects)))

        self.wait(3)