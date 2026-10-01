ARG NGINX_TAG=stable-alpine

#########################################################
# Set the base image to use for subsequent instructions #
#########################################################
FROM nginx:${NGINX_TAG} AS nginx


#########################################################
#          Create a run stage for development           #
#########################################################
FROM nginx AS development-run-stage

# Copy the development configuration files to the /etc/nginx/conf.d/ path inside the image.
COPY ./configs/development/ /etc/nginx/conf.d/
