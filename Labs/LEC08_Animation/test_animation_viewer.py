import unittest
from unittest.mock import Mock, patch

import animation_viewer as viewer


class AnimationViewerTests(unittest.TestCase):
    def test_sheet_rectangles_stay_inside_image_and_vary_in_size(self):
        sizes = set()
        for animation in viewer.ANIMATIONS:
            for frame in range(len(animation.frames)):
                x, y, width, height = viewer.source_rect(animation, frame)
                self.assertGreaterEqual(x, 0)
                self.assertGreaterEqual(y, 0)
                self.assertLessEqual(x + width, 6 * viewer.CELL_SIZE)
                self.assertLessEqual(y + height, 4 * viewer.CELL_SIZE)
                sizes.add((width, height))
                center_x, center_y, draw_width, draw_height = viewer.target_rect(animation, frame)
                self.assertGreaterEqual(draw_width, viewer.CANVAS_WIDTH // 2)
                self.assertGreaterEqual(draw_height, viewer.CANVAS_HEIGHT // 2)
                self.assertGreaterEqual(center_x - draw_width / 2, 0)
                self.assertLessEqual(center_x + draw_width / 2, viewer.CANVAS_WIDTH)
                self.assertGreaterEqual(center_y - draw_height / 2, 0)
                self.assertLessEqual(center_y + draw_height / 2, viewer.CANVAS_HEIGHT)
        self.assertGreater(len(sizes), 1)

    def test_overlapping_cells_keep_sword_tips_without_neighbor_artifacts(self):
        for animation, frame in ((viewer.RUN, 4), (viewer.RUN, 5), (viewer.ATTACK, 4)):
            x, _, _, _ = viewer.source_rect(animation, frame)
            self.assertGreaterEqual(x - animation.frames[frame] * viewer.CELL_SIZE, 34)
        for animation, frame in ((viewer.RUN, 3), (viewer.RUN, 4), (viewer.ATTACK, 3), (viewer.ATTACK, 4)):
            x, _, width, _ = viewer.source_rect(animation, frame)
            cell_right = (animation.frames[frame] + 1) * viewer.CELL_SIZE
            self.assertGreater(x + width, cell_right)

    def test_each_action_uses_its_own_frame_count_for_five_loops(self):
        self.assertEqual(len(viewer.ANIMATIONS), 4)
        for animation in viewer.ANIMATIONS:
            cycle = tuple(range(len(animation.frames)))
            self.assertEqual(viewer.playback_indices(animation), cycle * 5)
        self.assertEqual(len(viewer.playback_indices(viewer.ATTACK)), 25)

    def test_all_four_actions_pause_then_playback_restarts(self):
        grass = Mock()
        sprite = Mock(w=1536, h=1024)
        waits_in_one_round = sum(
            len(viewer.playback_indices(animation)) + 1
            for animation in viewer.ANIMATIONS
        )
        with (
            patch.object(viewer, 'open_canvas'),
            patch.object(viewer, 'close_canvas') as close_canvas,
            patch.object(viewer, 'load_image', side_effect=(grass, sprite)),
            patch.object(viewer, 'clear_canvas'),
            patch.object(viewer, 'update_canvas'),
            patch.object(viewer, 'exit_requested', return_value=False),
            patch.object(
                viewer, 'wait_or_exit',
                side_effect=[True] * waits_in_one_round + [False],
            ) as wait_or_exit,
        ):
            viewer.main()

        self.assertEqual(sprite.clip_draw.call_count, 116)
        self.assertEqual(
            sum(call.args == (viewer.PAUSE_SECONDS,) for call in wait_or_exit.call_args_list),
            4,
        )
        self.assertEqual(
            sprite.clip_draw.call_args.args[:4],
            viewer.source_rect(viewer.WALK, 0),
        )
        close_canvas.assert_called_once()


if __name__ == '__main__':
    unittest.main()
