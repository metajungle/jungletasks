# Jungletasks 

A simple Web application for keeping track of tasks. 

An example instance of the application is running at [http://tasks.metajungle.net][ref-tasks-metajungle]

This application is implemented using, supports and uses, the following technologies:

* The [Django][ref-django] Web Framework 
* The [Bootstrap][ref-bootstrap] Web front-end framework 
* The CSS extension framework [SASS][ref-sass] for improved CSS handling 
* Responsive design to better support mobile devices 
* The [jQuery][ref-jquery] JavaScript library
* The [Handlebars][ref-handlebars] JavaScript template library 

[ref-tasks-metajungle]: http://tasks.metajungle.net "Jungletasks"
[ref-django]: https://www.djangoproject.com/ "Django Web Framework"
[ref-sass]: http://sass-lang.com/ "SASS"
[ref-bootstrap]: http://getbootstrap.com/ "Bootstrap"
[ref-jquery]: http://jquery.com/ "jQuery JavaScript library"
[ref-handlebars]: http://handlebarsjs.com/ "Handlebars JavaScript library"

## Settings

The following can be configured in *settings.py*:

    JUNGLETASKS_DOMAIN = 'myapplication.com'

The domain and port where the application is running. Used for referring to the applications in email communication (e.g. account registration). Defaults to *localhost:8000* if Django's *DEBUG* setting is *True*.

    JUNGLETASKS_SEND_EMAIL_FROM = 'Jungle Tasks (No-Reply) <tasks@myapplication.net>'

The email address that the application uses to send emails from. The account the emails are sent from is configured using the standard Django *EMAIL\_\** settings. 

    JUNGLETASKS_SIGNUP_EMAIL_NOTIFICATION = False

*True* if the application should send emails to the application administrators when a user signs up, *False* otherwise. 

