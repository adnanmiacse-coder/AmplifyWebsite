from manim import *
config.background_color = BLACK

class Scene(MovingCameraScene):
    def construct(self):
        # Title Card
        title = Text("Mitosis: The Process of Cell Division", color=WHITE)
        self.play(Write(title))
        self.wait(3)
        self.play(FadeOut(title))
        self.wait(1.5)

        # Step 1: Introduction to the Cell
        cell_outer = Circle(radius=2, color=BLUE)
        cell_label = Text("Parent Cell", color=WHITE).next_to(cell_outer, UP)
        cytoplasm = Circle(radius=1.9, color=BLUE_D)
        nucleus_outer = Circle(radius=0.5, color=RED)
        nucleus_label = Text("Nucleus", color=WHITE).move_to(nucleus_outer.get_center() + DOWN * 0.7)
        chromosomes_in_nucleus = Group(
            Line(UP, DOWN, color=YELLOW, length=0.3),
            Line(UP, DOWN, color=YELLOW, length=0.3),
            Line(UP, DOWN, color=YELLOW, length=0.3)
        ).arrange(RIGHT, buff=0.2).move_to(nucleus_outer.get_center())
        chromosomes_label = Text("Chromosomes", color=WHITE).move_to(chromosomes_in_nucleus.get_center() + UP * 0.7)

        self.play(Create(cell_outer))
        self.play(FadeIn(cytoplasm))
        self.play(Create(nucleus_outer))
        self.play(Write(cell_label), Write(nucleus_label))
        self.play(Create(chromosomes_in_nucleus), Write(chromosomes_label))
        self.wait(3)

        # Step 2: Chromosome Replication (Interphase)
        self.play(self.camera.frame.animate.scale(1.2))
        self.play(self.camera.frame.animate.move_to(nucleus_outer.get_center()))
        self.wait(1.5)

        # Show replication of chromosomes
        replicated_chromosomes = Group()
        for chrom in chromosomes_in_nucleus:
            new_chrom = VGroup(
                Line(UP, DOWN, color=YELLOW, length=0.3).shift(LEFT*0.15),
                Line(UP, DOWN, color=YELLOW, length=0.3).shift(RIGHT*0.15)
            ).arrange(RIGHT, buff=0.05).move_to(chrom.get_center())
            replicated_chromosomes.add(new_chrom)

        replication_arrow = Arrow(chromosomes_in_nucleus.get_bottom(), replicated_chromosomes.get_top(), buff=0.1, color=GREEN)
        replication_text = Text("Replication", color=GREEN).next_to(replication_arrow, RIGHT)

        self.play(Transform(chromosomes_in_nucleus, replicated_chromosomes))
        self.play(GrowArrow(replication_arrow), Write(replication_text))
        self.wait(3)
        self.play(FadeOut(replication_arrow, replication_text))
        self.wait(1.5)

        # Step 3: Prophase - Chromosomes Condense
        self.play(self.camera.frame.animate.scale(1/1.2))
        self.play(self.camera.frame.animate.move_to(ORIGIN))
        self.wait(1.5)

        condensed_chromosomes = Group()
        for chrom in chromosomes_in_nucleus:
            condensed_chrom = VGroup(
                Line(UP, DOWN, color=YELLOW, length=0.5),
                Line(UP, DOWN, color=YELLOW, length=0.5)
            ).arrange(RIGHT, buff=0.1).move_to(chrom.get_center())
            condensed_chromosomes.add(condensed_chrom)

        prophase_text = Text("Prophase: Chromosomes condense", color=ORANGE).next_to(cell_outer, DOWN)
        self.play(Transform(chromosomes_in_nucleus, condensed_chromosomes))
        self.play(Write(prophase_text))
        self.wait(3)

        # Step 4: Metaphase - Alignment
        spindle_fibers_left = Line(LEFT*2, LEFT*1, color=PURPLE)
        spindle_fibers_right = Line(RIGHT*2, RIGHT*1, color=PURPLE)
        spindle_fibers_left2 = Line(LEFT*2, LEFT*1, color=PURPLE)
        spindle_fibers_right2 = Line(RIGHT*2, RIGHT*1, color=PURPLE)

        spindle_left = VGroup(spindle_fibers_left, spindle_fibers_left2).arrange(DOWN, buff=0.3).move_to(LEFT*1.5)
        spindle_right = VGroup(spindle_fibers_right, spindle_fibers_right2).arrange(DOWN, buff=0.3).move_to(RIGHT*1.5)

        metaphase_text = Text("Metaphase: Chromosomes align", color=ORANGE).next_to(cell_outer, DOWN)
        self.play(FadeOut(prophase_text), Write(metaphase_text))
        self.play(GrowFromPoint(spindle_left, spindle_left.get_center()))
        self.play(GrowFromPoint(spindle_right, spindle_right.get_center()))

        # Attach chromosomes to spindle fibers
        for i, chrom in enumerate(chromosomes_in_nucleus):
            dot_left = Dot(color=YELLOW).move_to(spindle_left[i].get_end())
            dot_right = Dot(color=YELLOW).move_to(spindle_right[i].get_end())
            self.play(
                chrom.animate.move_to(ORIGIN),
                dot_left.animate.move_to(chrom.get_left()),
                dot_right.animate.move_to(chrom.get_right())
            )
        self.wait(3)


        # Step 5: Anaphase - Separation
        anaphase_text = Text("Anaphase: Sister chromatids separate", color=ORANGE).next_to(cell_outer, DOWN)
        sep_chromosomes = Group()
        for i, chrom in enumerate(chromosomes_in_nucleus):
            part1 = Line(color=YELLOW, length=0.25).move_to(chrom.get_center() + LEFT*0.2)
            part2 = Line(color=YELLOW, length=0.25).move_to(chrom.get_center() + RIGHT*0.2)
            sep_chromosomes.add(part1, part2)

        self.play(FadeOut(metaphase_text), Write(anaphase_text))
        self.play(
            Transform(chromosomes_in_nucleus, sep_chromosomes),
            spindle_left.animate.move_to(LEFT * 2.5),
            spindle_right.animate.move_to(RIGHT * 2.5)
        )
        self.wait(3)

        # Step 6: Telophase & Cytokinesis - Two New Cells
        telophase_text = Text("Telophase & Cytokinesis", color=ORANGE).next_to(cell_outer, DOWN)
        cell_outer_2 = Circle(radius=2, color=BLUE).shift(RIGHT*3)
        cytoplasm_2 = Circle(radius=1.9, color=BLUE_D).shift(RIGHT*3)
        nucleus_outer_2a = Circle(radius=0.5, color=RED).shift(RIGHT*3 + UP*1)
        nucleus_outer_2b = Circle(radius=0.5, color=RED).shift(RIGHT*3 + DOWN*1)

        chromosomes_2a = Group(
            Line(UP, DOWN, color=YELLOW, length=0.3),
            Line(UP, DOWN, color=YELLOW, length=0.3),
            Line(UP, DOWN, color=YELLOW, length=0.3)
        ).arrange(RIGHT, buff=0.2).move_to(nucleus_outer_2a.get_center())

        chromosomes_2b = Group(
            Line(UP, DOWN, color=YELLOW, length=0.3),
            Line(UP, DOWN, color=YELLOW, length=0.3),
            Line(UP, DOWN, color=YELLOW, length=0.3)
        ).arrange(RIGHT, buff=0.2).move_to(nucleus_outer_2b.get_center())

        self.play(FadeOut(anaphase_text), Write(telophase_text))
        self.play(
            cell_outer.animate.shift(LEFT*3),
            cytoplasm.animate.shift(LEFT*3),
            nucleus_outer.animate.shift(LEFT*3),
            chromosomes_in_nucleus.animate.shift(LEFT*3)
        )
        self.play(
            FadeIn(cell_outer_2),
            FadeIn(cytoplasm_2),
            Create(nucleus_outer_2a),
            Create(nucleus_outer_2b),
            Transform(chromosomes_in_nucleus, chromosomes_2a).move_to(nucleus_outer_2a.get_center()),
            FadeIn(chromosomes_2b).move_to(nucleus_outer_2b.get_center()),
            spindle_left.animate.fadeOut(),
            spindle_right.animate.fadeOut()
        )
        self.wait(3)

        # Summary
        summary_text = Text("Mitosis creates two identical daughter cells", color=YELLOW).scale(0.8).move_to(UP*3)
        self.play(Write(summary_text))
        self.wait(4)

        # Final Fade Out
        self.play(
            FadeOut(cell_outer, cell_outer_2, cytoplasm, cytoplasm_2,
                    nucleus_outer, nucleus_outer_2a, nucleus_outer_2b,
                    chromosomes_in_nucleus, chromosomes_2a, chromosomes_2b,
                    summary_text)
        )
        self.wait(3)