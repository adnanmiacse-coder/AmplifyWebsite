from manim import *

config.background_color = BLACK

class Scene(MovingCameraScene):
    def construct(self):
        title = Text("Equation Division", font_size=60)
        self.play(Write(title))
        self.wait(1)
        self.play(FadeOut(title))

        eq1 = MathTex("a + b = c").scale(3)
        self.play(Write(eq1))
        self.wait(1)

        div_symbol = MathTex("\div").scale(3)
        self.play(FadeIn(div_symbol, shift=DOWN))
        self.wait(1)

        self.play(
            eq1.animate.scale(0.5).to_edge(UP),
            div_symbol.animate.scale(0.5).next_to(eq1, DOWN, buff=0.5)
        )
        self.wait(1)

        group = VGroup(eq1, div_symbol)

        eq2_left = MathTex("a", "+", "b", "=", "c").scale(2.5)
        eq2_right = MathTex("2", " ", " ", " ", " ").scale(2.5)

        arrow1 = Arrow(start=group.get_center() + DOWN * 0.5, end=eq2_left.get_center() + UP * 0.5, buff=0.2)
        arrow2 = Arrow(start=group.get_center() + DOWN * 0.5, end=eq2_right.get_center() + UP * 0.5, buff=0.2)

        self.play(Create(arrow1), Write(eq2_left))
        self.wait(1)
        self.play(Create(arrow2), Write(eq2_right))
        self.wait(2)

        self.play(FadeOut(group), FadeOut(arrow1), FadeOut(arrow2))
        self.play(FadeOut(eq2_left), FadeOut(eq2_right))

        final_eq = MathTex(r"\frac{a+b}{2} = \frac{c}{2}").scale(3)
        self.play(Write(final_eq))
        self.wait(2)
        self.play(FadeOut(final_eq))

        self.wait(2)