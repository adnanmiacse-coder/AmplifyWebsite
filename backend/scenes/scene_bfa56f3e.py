from manim import *

config.background_color = BLACK

class Scene(Scene):
    def construct(self):
        title = Text("Biology Exam Prep", font_size=48)
        self.play(Write(title))
        self.wait(1)
        self.play(FadeOut(title))

        bio_text = Text("Biology:", font_size=40, color=GREEN)
        exam_text = Text("Exam Practice", font_size=40, color=BLUE)
        vgroup = VGroup(bio_text, exam_text).arrange(RIGHT, buff=0.5)

        self.play(Write(vgroup))
        self.wait(1)

        circle = Circle(radius=0.5, color=YELLOW)
        square = Square(side_length=1, color=RED)
        arrow = Arrow(start=UP, end=DOWN, color=WHITE)

        shapes = VGroup(circle, square, arrow).arrange(DOWN, buff=1)

        intro_text = Text("Let's practice!", font_size=30, color=WHITE).next_to(shapes, DOWN, buff=1)

        self.play(Create(shapes))
        self.play(Write(intro_text))
        self.wait(2)
        self.play(FadeOut(VGroup(vgroup, shapes, intro_text)))

        question_text = Text("Question 1: Which organelle is...", font_size=24, color=WHITE)
        options_text = Text("A) Nucleus B) Mitochondria C) Ribosome", font_size=20, color=WHITE).next_to(question_text, DOWN, buff=0.5)
        
        self.play(Write(question_text))
        self.play(Write(options_text))
        self.wait(2)

        correct_answer = Text("C) Ribosome", font_size=24, color=GREEN).next_to(options_text, DOWN, buff=0.7)
        self.play(FadeIn(correct_answer))
        self.wait(2)

        self.play(FadeOut(VGroup(question_text, options_text, correct_answer)))
        self.wait(2)

        math_tex_example = MathTex(r"\text{Cellular Respiration: } C_6H_{12}O_6 + 6O_2 \rightarrow 6CO_2 + 6H_2O", font_size=30, color=WHITE)
        self.play(Write(math_tex_example))
        self.wait(2)
        self.play(FadeOut(math_tex_example))
        self.wait(2)

        final_message = Text("Keep practicing!", font_size=36, color=YELLOW)
        self.play(Write(final_message))
        self.wait(2)
        self.play(FadeOut(final_message))
        self.wait(2)