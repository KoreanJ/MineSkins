FROM ucsdets/scipy-ml-notebook:2019.4-stable

LABEL maintainer="Nick Smith <nrs003@ucsd.edu>"

ENV CHROME_VER=2.44
ENV FIREFOX_VER=v0.23.0

# Set when building on Travis so that certain long-running build steps can
# be skipped to shorten build time.
ARG TEST_ONLY_BUILD

USER root

# Chrome and Firefox browsers
RUN apt-get update && \
	apt-get install -y gnupg && \
	wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add - && \
	sh -c 'echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list' && \
	apt-get update && apt-get install -y google-chrome-stable firefox

USER $NB_UID

# Selenium
RUN pip install selenium

# Chrome driver
#RUN CHROME_VER=$(wget -qO- https://chromedriver.storage.googleapis.com/LATEST_RELEASE) && \
RUN wget -q https://chromedriver.storage.googleapis.com/${CHROME_VER}/chromedriver_linux64.zip && \
	unzip -o chromedriver_linux64.zip && \
	rm chromedriver_linux64.zip && \
	mv chromedriver /opt/conda/bin

# Firefox driver
#RUN FIREFOX_VER=$(wget -qO- https://api.github.com/repos/mozilla/geckodriver/releases/latest | grep -Po '"tag_name": "\K.*?(?=")') && \
RUN wget -qO- https://github.com/mozilla/geckodriver/releases/download/${FIREFOX_VER}/geckodriver-${FIREFOX_VER}-linux64.tar.gz | tar -xvz -C /opt/conda/bin


EXPOSE 4444
