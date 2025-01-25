;;; rime-wubi-dict-adder.el --- Description -*- lexical-binding: t; -*-
;;
;; Copyright (C) 2025 xinyu
;;
;; Author: xinyu <xinyu@maotu>
;; Maintainer: xinyu <xinyu@maotu>
;; Created: janvier 25, 2025
;; Modified: janvier 25, 2025
;; Version: 0.0.1
;; Keywords: abbrev bib c calendar comm convenience data docs emulations extensions faces files frames games hardware help hypermedia i18n internal languages lisp local maint mail matching mouse multimedia news outlines processes terminals tex tools unix vc wp
;; Homepage: https://github.com/xinyu/rime-wubi-dict-adder
;; Package-Requires: ((emacs "24.3"))
;;
;; This file is not part of GNU Emacs.
;;
;;; Commentary:
;;
;;  This file defined a function to add a word and its code to the rime-wubi dictionary.
;;
;;; Code:

(defvar rime-wubi-dict-adder-user-dict "~/.config/ibus/rime/wubi86_jidian.user.dict.yaml")
(defvar rime-wubi-dict-adder-python-command "python")
(defvar rime-wubi-dict-adder-script-path "dictAdder.py")
(defun rime-wubi-dict-adder (word code)
  "Add a word and its code to the rime-wubi dictionary."
  (interactive "sWord: \nsCode: ")
  (with-temp-buffer
    (insert (format "%s\t%s\n" word code))
    (write-region (point-min) (point-max)  t)))

(defun rime-wubi-dict-adder-with-python (word)
  "Add a word and its code to the rime-wubi dictionary using Python."
  (interactive "sWord: ")
  (let ((command (format "%s %s %s" rime-wubi-dict-adder-python-command rime-wubi-dict-adder-script-path word)))
    (shell-command command)))

(defun rime-wubi-dict-adder-from-selected-region ()
  "Add a word and its code to the rime-wubi dictionary using Python."
  (interactive)
  (let ((word (buffer-substring-no-properties (region-beginning) (region-end))))
    (rime-wubi-dict-adder-with-python word)))

(provide 'rime-wubi-dict-adder)
;;; rime-wubi-dict-adder.el ends here
