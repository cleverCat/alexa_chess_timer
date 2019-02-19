# -*- coding: utf-8 -*-
"""Simple fact sample app."""

import random
import logging

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import (
    AbstractRequestHandler, AbstractExceptionHandler,
    AbstractRequestInterceptor, AbstractResponseInterceptor)
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model.ui import SimpleCard
from ask_sdk_model import Response
from chess_timer import ChessTimer


# =========================================================================================================================================
# TODO: The items below this comment need your attention.
# =========================================================================================================================================
SKILL_NAME = "chess"
HELP_MESSAGE = "To start a timer, please respond with word step. To quit game say exit game. In any moment of game I can tell the time of each players turns, on request with word statistic. First color will be blue. Yall ready?"
HELP_REPROMPT = "Just say step to start the timer. "
STOP_MESSAGE = "We will play another time. Goodbye!"
FALLBACK_MESSAGE = "Sorry, I don't know that." + HELP_REPROMPT
FALLBACK_REPROMPT = "What can I help you with?" + HELP_REPROMPT
EXCEPTION_MESSAGE = "Sorry. I cannot help you with that."
STEP_MESSAGE = 'It\'s {0} turn,'
JOKE_LIST = [
    'May the Force be with {0}',
    'Stay awhile and listen',
    'Hold his beer',
    'As the prophecy foretold',
    'It is super effective',
    'Party is over',
    'Brace yourselves, {0} is coming',
    'I could calculate your chance of survival, {0}, but you will not like it”',
    'Release the Kraken',
    'Just as planned',
    'Oh what a day. What a lovely day',
    'Look at {0}. He is the captain now',
    'Are you not entertained?',
    'May the odds ever be in your favor',
    'Why so serious, {0}?',    
    'Just keep swimming, {0}',
    'You are a wizard, {0}',
    'Here is {0}!',
    'A wild {0} appeared',
    'The only way to win is not to play, {0}',
    'Do you feel in charge, {0}?'
    ]


# =========================================================================================================================================
# Editing anything below this line might break your skill.
# =========================================================================================================================================

sb = SkillBuilder()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def get_statistic(session):
    chess_timer = ChessTimer(session)
    def get_statistic_time(_time):
        from datetime import timedelta
        current_time_delta = timedelta(seconds=_time)
        current_minutes = current_time_delta.seconds // 60 % 60
        current_seconds = current_time_delta.seconds - current_minutes * 60 
        return 'minutes ' + str(current_minutes) + ' seconds ' + str(current_seconds)
    statistic = chess_timer.get_statistic()
    list_statistic = [str(player) + ' ' + get_statistic_time(_time) + ' ' for player, _time in statistic.items()]
    speech = ' '.join(list_statistic)
    return speech


class StartHandle(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_request_type("LaunchRequest")(handler_input) 
    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In GetStartHandler")
        session = handler_input.attributes_manager.session_attributes
        chess_timer = ChessTimer(session)
        reprompt = "Say yes to start the game or no to quit."
        handler_input.response_builder.speak(HELP_MESSAGE).ask(reprompt)
        return handler_input.response_builder.response

class GetStatisticHandle(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("chess_statistic")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In GetStatisticHandle")
        session = handler_input.attributes_manager.session_attributes
        speech = get_statistic(session)
        handler_input.response_builder.speak(speech).ask('help text')
        return handler_input.response_builder.response

       
class GetStepHandle(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("chess_step")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In GetStepHandle")
        session = handler_input.attributes_manager.session_attributes
        chess_timer = ChessTimer(session)
       
        new_session = chess_timer.step()

        handler_input.attributes_manager.session_attributes = new_session
        logger.info(new_session['current_player_name'])
         
        logger.info(STEP_MESSAGE + ' ' + random.choice(JOKE_LIST))
        handler_input.response_builder.speak((STEP_MESSAGE + ' ' + random.choice(JOKE_LIST)).format(new_session['current_player_name'])).ask('hello')
        return handler_input.response_builder.response
       


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In HelpIntentHandler")

        handler_input.response_builder.speak(HELP_MESSAGE).ask(
            HELP_REPROMPT).set_card(SimpleCard(
                SKILL_NAME, HELP_MESSAGE))
        return handler_input.response_builder.response


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (is_intent_name("AMAZON.CancelIntent")(handler_input) or
                is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In CancelOrStopIntentHandler")
        session = handler_input.attributes_manager.session_attributes
        speech = get_statistic(session)

        handler_input.response_builder.speak(speech + STOP_MESSAGE)
        return handler_input.response_builder.response


class FallbackIntentHandler(AbstractRequestHandler):
    """Handler for Fallback Intent.

    AMAZON.FallbackIntent is only available in en-US locale.
    This handler will not be triggered except in that locale,
    so it is safe to deploy on any locale.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In FallbackIntentHandler")

        handler_input.response_builder.speak(FALLBACK_MESSAGE).ask(
            FALLBACK_REPROMPT)
        return handler_input.response_builder.response


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In SessionEndedRequestHandler")

        logger.info("Session ended reason: {}".format(
            handler_input.request_envelope.request.reason))
        return handler_input.response_builder.response


# Exception Handler
class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Catch all exception handler, log exception and
    respond with custom message.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.info("In CatchAllExceptionHandler")
        logger.error(exception, exc_info=True)

        handler_input.response_builder.speak(EXCEPTION_MESSAGE).ask(
            HELP_REPROMPT)

        return handler_input.response_builder.response


# Request and Response loggers
class RequestLogger(AbstractRequestInterceptor):
    """Log the alexa requests."""
    def process(self, handler_input):
        # type: (HandlerInput) -> None
        logger.debug("Alexa Request: {}".format(
            handler_input.request_envelope.request))


class ResponseLogger(AbstractResponseInterceptor):
    """Log the alexa responses."""
    def process(self, handler_input, response):
        # type: (HandlerInput, Response) -> None
        logger.debug("Alexa Response: {}".format(response))


# Register intent handlers
sb.add_request_handler(StartHandle())
sb.add_request_handler(GetStepHandle())
sb.add_request_handler(GetStatisticHandle())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())

# Register exception handlers
sb.add_exception_handler(CatchAllExceptionHandler())

# TODO: Uncomment the following lines of code for request, response logs.
# sb.add_global_request_interceptor(RequestLogger())
# sb.add_global_response_interceptor(ResponseLogger())

# Handler name that is used on AWS lambda
lambda_handler = sb.lambda_handler()
