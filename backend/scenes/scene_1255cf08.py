from manim import *
config.background_color = BLACK

class Scene(MovingCameraScene):
    def construct(self):
        # Title Card
        title = Text("Cell Division", color=WHITE)
        title.scale(1.5)
        self.play(Write(title))
        self.wait(2)
        self.play(FadeOut(title))
        self.wait(1)

        # Step 1: Introduction to Cells
        cell1 = Circle(radius=1, color=BLUE)
        cell1_label = Text("Parent Cell", color=WHITE, font_size=24).next_to(cell1, DOWN)
        self.play(GrowFromCenter(cell1), Write(cell1_label))
        self.wait(2)

        explanation1 = Text("All living things are made of cells.", color=YELLOW, font_size=28).to_edge(UP)
        self.play(Write(explanation1))
        self.wait(3)
        self.play(FadeOut(explanation1))

        # Step 2: The Need for Division
        growth_arrow = Arrow(ORIGIN, UP, color=GREEN)
        growth_label = Text("Growth & Repair", color=WHITE, font_size=24).next_to(growth_arrow, UP)
        self.play(GrowArrow(growth_arrow), Write(growth_label))
        self.wait(2)

        multiplication_text = Text("Cells need to multiply to create new organisms.", color=YELLOW, font_size=28).to_edge(UP)
        self.play(Write(multiplication_text))
        self.wait(3)
        self.play(FadeOut(growth_arrow, growth_label, multiplication_text))

        # Step 3: Mitosis - Chromosome Duplication
        self.play(self.camera.frame.animate.scale(0.8).move_to(cell1))
        self.wait(1)

        chromosomes = VGroup(
            Line(LEFT*0.2, RIGHT*0.2, color=RED),
            Line(LEFT*0.2, RIGHT*0.2, color=RED)
        ).arrange(DOWN, buff=0.2).move_to(cell1.get_center())
        chromosomes_label = Text("Chromosomes (DNA)", color=WHITE, font_size=24).next_to(chromosomes, UP)
        self.play(
            FadeOut(cell1_label),
            ReplacementTransform(cell1, Cell(radius=1, color=BLUE)),
            Write(chromosomes_label),
            Create(chromosomes[0]),
            Create(chromosomes[1])
        )
        self.wait(2)

        duplicated_chromosomes = VGroup(
            Line(LEFT*0.2, RIGHT*0.2, color=RED),
            Line(LEFT*0.2, RIGHT*0.2, color=RED)
        ).arrange(DOWN, buff=0.2).move_to(cell1.get_center())
        duplicated_chromosomes[0].set_x(-0.2)
        duplicated_chromosomes[1].set_x(0.2)
        duplicated_chromosomes[0].rotate(PI/4, about_point=duplicated_chromosomes[0].get_center())
        duplicated_chromosomes[1].rotate(-PI/4, about_point=duplicated_chromosomes[1].get_center())

        self.play(Indicate(chromosomes, color=YELLOW, scale_factor=1.5), run_time=1)
        self.wait(1)

        duplication_text = Text("DNA replicates (duplicates) within the nucleus.", color=YELLOW, font_size=28).to_edge(UP)
        self.play(Write(duplication_text))
        self.wait(3)
        self.play(FadeOut(duplication_text))

        # Step 4: Mitosis - Chromosomes Align and Separate
        # Showing duplicated chromosomes as X shapes
        x_chromosomes = VGroup()
        x1 = Line(LEFT*0.3, RIGHT*0.3, color=RED).rotate(PI/4)
        x2 = Line(LEFT*0.3, RIGHT*0.3, color=RED).rotate(-PI/4)
        x_chromosomes.add(x1, x2)
        x_chromosomes.move_to(cell1.get_center())
        chromosomes_aligned_label = Text("Duplicated Chromosomes", color=WHITE, font_size=24).next_to(x_chromosomes, UP)

        self.play(
            FadeOut(chromosomes_label),
            ReplacementTransform(VGroup(chromosomes[0], chromosomes[1]), x_chromosomes),
            Write(chromosomes_aligned_label)
        )
        self.wait(2)

        # Aligning in the middle
        middle_line = Line(LEFT*2, RIGHT*2, color=GRAY).move_to(cell1.get_center())
        self.play(Create(middle_line))
        self.wait(1)

        # Arrows showing separation
        arrow_up = Arrow(middle_line.get_right(), UP, color=PURPLE)
        arrow_down = Arrow(middle_line.get_left(), DOWN, color=PURPLE)
        self.play(GrowArrow(arrow_up), GrowArrow(arrow_down))
        self.wait(2)

        separation_text = Text("Chromosomes align and then separate into two identical sets.", color=YELLOW, font_size=28).to_edge(UP)
        self.play(Write(separation_text))
        self.wait(3)
        self.play(FadeOut(separation_text, middle_line, arrow_up, arrow_down))

        # Step 5: Mitosis - Cell Splits
        cell1.set_fill(BLUE, opacity=0.8)
        divided_cell_left = Circle(radius=0.7, color=BLUE).shift(LEFT*0.5)
        divided_cell_right = Circle(radius=0.7, color=BLUE).shift(RIGHT*0.5)
        divided_cell_left_label = Text("Daughter Cell 1", color=WHITE, font_size=24).next_to(divided_cell_left, DOWN)
        divided_cell_right_label = Text("Daughter Cell 2", color=WHITE, font_size=24).next_to(divided_cell_right, DOWN)

        self.play(
            ReplacementTransform(x_chromosomes, VGroup(
                Line(LEFT*0.15, RIGHT*0.15, color=RED).rotate(PI/4).move_to(divided_cell_left.get_center()),
                Line(LEFT*0.15, RIGHT*0.15, color=RED).rotate(-PI/4).move_to(divided_cell_left.get_center())
            )),
            ReplacementTransform(x_chromosomes, VGroup(
                Line(LEFT*0.15, RIGHT*0.15, color=RED).rotate(PI/4).move_to(divided_cell_right.get_center()),
                Line(LEFT*0.15, RIGHT*0.15, color=RED).rotate(-PI/4).move_to(divided_cell_right.get_center())
            )),
            Transform(cell1, divided_cell_left),
            FadeIn(divided_cell_left_label),
            Transform(cell1, divided_cell_right), # This is a bit of a hack to make it appear on the right
            FadeIn(divided_cell_right_label),
            run_time=3
        )
        self.wait(2)
        split_text = Text("The cell splits into two genetically identical daughter cells.", color=YELLOW, font_size=28).to_edge(UP)
        self.play(Write(split_text))
        self.wait(4)
        self.play(FadeOut(split_text, chromosomes_aligned_label))

        # Step 6: Meiosis (Briefly)
        self.play(self.camera.frame.animate.scale(1.2).move_to(ORIGIN))
        parent_cell_meiosis = Circle(radius=1, color=TEAL).shift(LEFT*2)
        parent_cell_meiosis_label = Text("Starting Cell", color=WHITE, font_size=24).next_to(parent_cell_meiosis, DOWN)
        self.play(FadeIn(parent_cell_meiosis), Write(parent_cell_meiosis_label))
        self.wait(2)

        meiosis_arrow = Arrow(parent_cell_meiosis.get_right(), RIGHT*2, color=ORANGE)
        meiosis_arrow_label = Text("Meiosis", color=WHITE, font_size=24).next_to(meiosis_arrow, UP)
        self.play(GrowArrow(meiosis_arrow), Write(meiosis_arrow_label))
        self.wait(2)

        daughter_cell_1 = Circle(radius=0.5, color=GREEN).shift(RIGHT*2.5)
        daughter_cell_2 = Circle(radius=0.5, color=GREEN).shift(RIGHT*1.5)
        daughter_cell_3 = Circle(radius=0.5, color=GREEN).shift(RIGHT*3.5)
        daughter_cell_4 = Circle(radius=0.5, color=GREEN).shift(RIGHT*0.5)
        daughter_cells = VGroup(daughter_cell_1, daughter_cell_2, daughter_cell_3, daughter_cell_4)
        daughter_cells_label = Text("Gametes (Sex Cells)", color=WHITE, font_size=24).next_to(daughter_cells, DOWN)

        self.play(
            FadeOut(parent_cell_meiosis_label, meiosis_arrow_label),
            FadeOut(parent_cell_meiosis),
            FadeIn(daughter_cells),
            Write(daughter_cells_label)
        )
        self.wait(3)

        meiosis_explanation = Text("Meiosis produces gametes (sex cells) with half the DNA.", color=YELLOW, font_size=28).to_edge(UP)
        self.play(Write(meiosis_explanation))
        self.wait(4)
        self.play(FadeOut(meiosis_explanation))

        # Summary
        summary_title = Text("Key Takeaway:", color=GOLD).to_edge(UP)
        summary_point1 = Text("Mitosis: For growth, repair, and asexual reproduction. Creates identical cells.", color=WHITE, font_size=24).next_to(summary_title, DOWN, buff=0.5)
        summary_point2 = Text("Meiosis: For sexual reproduction. Creates genetically diverse gametes.", color=WHITE, font_size=24).next_to(summary_point1, DOWN, buff=0.5)

        self.play(Write(summary_title))
        self.play(Write(summary_point1))
        self.wait(3)
        self.play(Write(summary_point2))
        self.wait(5)

        self.play(FadeOut(*self.mobjects))
        self.wait(3)