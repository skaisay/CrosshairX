"""
Crosshair rendering engine.
Draws different crosshair styles using QPainter with GPU acceleration via OpenGL.
"""

import math
from PyQt5.QtCore import QPointF, QRectF
from PyQt5.QtGui import QPainter, QPen, QColor, QBrush, QPolygonF


class CrosshairRenderer:
    """Renders various crosshair styles onto a QPainter."""

    def __init__(self):
        self._style_map = {
            "cross": self._draw_cross,
            "dot": self._draw_dot,
            "circle": self._draw_circle,
            "chevron": self._draw_chevron,
            "diamond": self._draw_diamond,
            "crossdot": self._draw_crossdot,
            "triangle": self._draw_triangle,
            "crosshair_classic": self._draw_classic,
        }

    def draw(self, painter: QPainter, center_x: float, center_y: float, config: dict,
             anim_state: dict | None = None):
        """
        Draw the crosshair at the given center point.

        Args:
            painter: QPainter to draw on
            center_x, center_y: Center coordinates
            config: Crosshair config dict
            anim_state: Animation state dict (color_override, size_mult, rotation, gap_offset, opacity)
        """
        if anim_state is None:
            anim_state = {}

        style = config.get("style", "cross")
        base_size = config.get("size", 20)
        thickness = config.get("thickness", 2)
        gap = config.get("gap", 4)
        color = list(config.get("color", [0, 255, 0, 255]))
        outline = config.get("outline", True)
        outline_color = config.get("outline_color", [0, 0, 0, 180])
        outline_thickness = config.get("outline_thickness", 1)
        show_dot = config.get("dot", True)
        dot_size = config.get("dot_size", 2)
        t_style = config.get("t_style", False)

        # Apply animation modifiers
        size_mult = anim_state.get("size_mult", 1.0)
        rotation = anim_state.get("rotation", 0.0)
        gap_offset = anim_state.get("gap_offset", 0.0)
        opacity_mult = anim_state.get("opacity", 1.0)
        color_override = anim_state.get("color_override", None)

        size = base_size * size_mult
        gap = gap + gap_offset

        if color_override:
            color = list(color_override)

        color[3] = int(color[3] * opacity_mult)

        qcolor = QColor(color[0], color[1], color[2], color[3])
        qoutline = QColor(outline_color[0], outline_color[1], outline_color[2], outline_color[3])

        # Save painter state
        painter.save()
        painter.setRenderHint(QPainter.Antialiasing, True)

        # Apply rotation
        if rotation != 0:
            painter.translate(center_x, center_y)
            painter.rotate(rotation)
            painter.translate(-center_x, -center_y)

        draw_fn = self._style_map.get(style, self._draw_cross)

        # Draw outline first (if enabled)
        if outline:
            outline_pen = QPen(qoutline, thickness + outline_thickness * 2)
            outline_pen.setCapStyle(2)  # Qt.RoundCap = 0x20, FlatCap = 0x00, SquareCap = 0x10
            draw_fn(painter, center_x, center_y, size, thickness + outline_thickness * 2,
                     gap, qoutline, show_dot, dot_size + outline_thickness, t_style)

        # Draw main crosshair
        draw_fn(painter, center_x, center_y, size, thickness, gap,
                qcolor, show_dot, dot_size, t_style)

        painter.restore()

    # ===================== CROSSHAIR STYLES =====================

    def _draw_cross(self, painter, cx, cy, size, thickness, gap, color, dot, dot_size, t_style):
        """Classic cross/plus crosshair."""
        pen = QPen(color, thickness)
        pen.setCapStyle(0x10)  # SquareCap
        painter.setPen(pen)

        half = size / 2

        # Right
        painter.drawLine(QPointF(cx + gap, cy), QPointF(cx + half, cy))
        # Left
        painter.drawLine(QPointF(cx - gap, cy), QPointF(cx - half, cy))
        # Bottom
        painter.drawLine(QPointF(cx, cy + gap), QPointF(cx, cy + half))
        # Top (skip if T-style)
        if not t_style:
            painter.drawLine(QPointF(cx, cy - gap), QPointF(cx, cy - half))

        if dot and dot_size > 0:
            painter.setPen(QPen(color, 1))
            painter.setBrush(QBrush(color))
            painter.drawEllipse(QPointF(cx, cy), dot_size, dot_size)

    def _draw_dot(self, painter, cx, cy, size, thickness, gap, color, dot, dot_size, t_style):
        """Single dot crosshair."""
        radius = max(dot_size, size / 4)
        painter.setPen(QPen(color, 1))
        painter.setBrush(QBrush(color))
        painter.drawEllipse(QPointF(cx, cy), radius, radius)

    def _draw_circle(self, painter, cx, cy, size, thickness, gap, color, dot, dot_size, t_style):
        """Circle crosshair."""
        pen = QPen(color, thickness)
        painter.setPen(pen)
        painter.setBrush(QBrush())  # No fill
        radius = size / 2
        painter.drawEllipse(QPointF(cx, cy), radius, radius)

        if dot and dot_size > 0:
            painter.setBrush(QBrush(color))
            painter.drawEllipse(QPointF(cx, cy), dot_size, dot_size)

    def _draw_chevron(self, painter, cx, cy, size, thickness, gap, color, dot, dot_size, t_style):
        """Chevron/V-shape crosshair."""
        pen = QPen(color, thickness)
        pen.setCapStyle(0x20)  # RoundCap
        pen.setJoinStyle(0x80)  # RoundJoin
        painter.setPen(pen)

        half = size / 2
        offset = gap

        # Draw V shape
        polygon = QPolygonF([
            QPointF(cx - half, cy - half / 2 + offset),
            QPointF(cx, cy + offset),
            QPointF(cx + half, cy - half / 2 + offset),
        ])
        painter.drawPolyline(polygon)

        if dot and dot_size > 0:
            painter.setBrush(QBrush(color))
            painter.setPen(QPen(color, 1))
            painter.drawEllipse(QPointF(cx, cy), dot_size, dot_size)

    def _draw_diamond(self, painter, cx, cy, size, thickness, gap, color, dot, dot_size, t_style):
        """Diamond shape crosshair."""
        pen = QPen(color, thickness)
        pen.setJoinStyle(0x00)  # MiterJoin
        painter.setPen(pen)
        painter.setBrush(QBrush())  # No fill

        half = size / 2
        polygon = QPolygonF([
            QPointF(cx, cy - half),       # Top
            QPointF(cx + half, cy),       # Right
            QPointF(cx, cy + half),       # Bottom
            QPointF(cx - half, cy),       # Left
            QPointF(cx, cy - half),       # Close
        ])
        painter.drawPolyline(polygon)

        if dot and dot_size > 0:
            painter.setBrush(QBrush(color))
            painter.setPen(QPen(color, 1))
            painter.drawEllipse(QPointF(cx, cy), dot_size, dot_size)

    def _draw_crossdot(self, painter, cx, cy, size, thickness, gap, color, dot, dot_size, t_style):
        """Cross with prominent center dot."""
        # Draw the cross
        self._draw_cross(painter, cx, cy, size, thickness, gap, color, False, 0, t_style)

        # Draw larger center dot
        radius = max(dot_size, 3)
        painter.setPen(QPen(color, 1))
        painter.setBrush(QBrush(color))
        painter.drawEllipse(QPointF(cx, cy), radius, radius)

    def _draw_triangle(self, painter, cx, cy, size, thickness, gap, color, dot, dot_size, t_style):
        """Triangle crosshair pointing up."""
        pen = QPen(color, thickness)
        pen.setJoinStyle(0x00)  # MiterJoin
        painter.setPen(pen)
        painter.setBrush(QBrush())

        half = size / 2
        h = half * math.sqrt(3) / 2

        polygon = QPolygonF([
            QPointF(cx, cy - h + gap),
            QPointF(cx + half, cy + h / 2 + gap),
            QPointF(cx - half, cy + h / 2 + gap),
            QPointF(cx, cy - h + gap),
        ])
        painter.drawPolyline(polygon)

        if dot and dot_size > 0:
            painter.setBrush(QBrush(color))
            painter.setPen(QPen(color, 1))
            painter.drawEllipse(QPointF(cx, cy), dot_size, dot_size)

    def _draw_classic(self, painter, cx, cy, size, thickness, gap, color, dot, dot_size, t_style):
        """Classic crosshair with circle + cross."""
        # Draw circle
        self._draw_circle(painter, cx, cy, size, thickness, gap, color, False, 0, t_style)
        # Draw cross lines extending from circle
        half = size / 2
        ext = half * 0.4
        pen = QPen(color, thickness)
        painter.setPen(pen)
        painter.drawLine(QPointF(cx - half - ext, cy), QPointF(cx - half, cy))
        painter.drawLine(QPointF(cx + half, cy), QPointF(cx + half + ext, cy))
        painter.drawLine(QPointF(cx, cy - half - ext), QPointF(cx, cy - half))
        painter.drawLine(QPointF(cx, cy + half), QPointF(cx, cy + half + ext))

        if dot and dot_size > 0:
            painter.setBrush(QBrush(color))
            painter.setPen(QPen(color, 1))
            painter.drawEllipse(QPointF(cx, cy), dot_size, dot_size)
