from enum import StrEnum


class UgcEndpoints(StrEnum):
    event_viewer_settings = "/event/viewer/settings"
    event_viewer_progress = "/event/viewer/progress"
    event_click = "/event/click"
    bookmark = "/bookmark/"
    review = "/review/"
    reaction_review = "/reaction/review"
    reaction_movie = "/reaction/movie"
