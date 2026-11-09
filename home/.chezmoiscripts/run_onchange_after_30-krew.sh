#!/bin/sh
# RBAC access matrices for reading EKS permissions from the terminal.
set -eu

kubectl krew update
kubectl krew install access-matrix rbac-tool
