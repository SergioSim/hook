FROM moodlehq/moodle-php-apache:8.1-bullseye

RUN chown -R ${DOCKER_USER:-1000} \
    /var/www/moodledata \
    /var/www/phpunitdata \
    /var/www/behatdata \
    /var/www/behatfaildumps \
    /usr/local/etc/php/conf.d

# Un-privileged user running the application
USER ${DOCKER_USER:-1000}

CMD ["apache2-foreground"]
ENTRYPOINT ["moodle-docker-php-entrypoint"]
