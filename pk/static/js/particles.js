/*----------------------------------------------------------
 * Copyright (c) 2015 PushingKarma. All rights reserved.
 *------------------------------------------------------- */
'use strict';

(function($) {

    $(function() {
        var canvas = $("#particles");
        var ctx = canvas.get()[0].getContext("2d");
        var header = canvas.parent();
        var width = 10;
        var height = 10;
        var particles = [];

        // Particle Object
        var Particle = function() {
            this.x = Math.random() * width;
            this.y = Math.random() * height;
            this.radius = 1;
            this.color = "255,255,255";
            this.opacity = (Math.random() * 0.4) + 0.2;
            this.direction = Math.floor(Math.random() * Math.PI*2);
            this.speed = null;
            this.turnin = null;

            this.init = function() {
                this.setSpeed();
                this.setTurns();
                return this;
            };
            this.checkBoundries = function() {
                if (this.x < - 5) this.x = width + 5;
                if (this.y < - 5) this.y = height + 5;
                if (this.x > width + 5) this.x = - 5;
                if (this.y > height + 5) this.y = - 5;
            };
            this.decrimentTurn = function() {
                this.turnin -= 1;
                if (this.turnin < 0) {
                    this.updateDirection();
                    this.setSpeed();
                    this.setTurns();
                }
            };
            this.draw = function() {
                ctx.beginPath();
                var gradient = ctx.createRadialGradient(this.x, this.y, 0, this.x, this.y, this.radius);
                gradient.addColorStop(0, "rgba("+this.color+","+this.opacity+")");
                gradient.addColorStop(1, "rgba("+this.color+",0)");
                ctx.fillStyle = gradient;
                ctx.arc(this.x, this.y, this.radius, Math.PI*2, false);
                ctx.fill();
            };
            this.setSpeed = function() { this.speed = (Math.random() * 0.3) + 0.1; };
            this.setTurns = function() { this.turnin = Math.floor(Math.random() * 80) + 20; };
            this.updateDirection = function() { this.direction += Math.random() * 0.5 * (Math.random()>0.5 ? 1:-1); };
            this.updatePosition = function() {
                this.x += Math.cos(this.direction) * this.speed;
                this.y += Math.sin(this.direction) * this.speed;
                this.checkBoundries();
                this.decrimentTurn();
            };
        };

        // Update the canvas size
        var updateCanvasSize = function() {
            var newWidth = Math.floor(header.width() / 2);
            var newHeight = Math.floor(header.height() / 2);
            if ((newWidth != width) || (newHeight != height) && (newHeight < 200)) {
                width = newWidth;
                height = newHeight;
                canvas.attr("width", width);
                canvas.attr("height", height);
                canvas.css({width:(width*2)+"px", height:(height*2)+"px"});
            }
        };

        // Animate the Particles
        var drawParticles = function() {
            updateCanvasSize();
            ctx.clearRect(0, 0, width, height);
            ctx.globalCompositeOperation = "lighter";
            for (var i=0; i<particles.length; i++) {
                var particle = particles[i];
                particle.draw();
                particle.updatePosition();
            }
        };

        // Return True if Canvas works
        function isCanvasSupported() {
            var elem = document.createElement("canvas");
            return !!(elem.getContext && elem.getContext("2d"));
        }

        // Create an array or particles
        if (isCanvasSupported()) {
            updateCanvasSize();
            var numparticles = Math.floor(width / 40);
            for (var i=0; i<numparticles; i++) { particles.push(new Particle().init()); }
            setInterval(drawParticles, 30);
        }
    });

})(window.jQuery);