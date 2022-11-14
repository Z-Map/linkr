ARG BASE_IMAGE_TAG=latest
FROM mapiou/arch-dev:${BASE_IMAGE_TAG} as dev

RUN ["sudo", "build-pacman", "-Syu", "tmux", "nodejs", "npm"]
