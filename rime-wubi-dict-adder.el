
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

(defvar rime-wubi-dict-adder-user-dict "~/.config/ibus/rime/wubi86_jidian_user.dict.yaml")
(setq rime-wubi-dict-adder-user-dict
  (cond
   ((string-equal system-type "darwin")
    "~/Library/Rime/wubi86_jidian_user.dict.yaml")
   ((string-equal system-type "gnu/linux")
    (if (file-exists-p "~/.config/ibus/rime/wubi86_jidian_user.dict.yaml")
        "~/.config/ibus/rime/wubi86_jidian_user.dict.yaml"
      "~/.local/share/fcitx5/rime/wubi86_jidian_user.dict.yaml")) ; default fcitx5 location
   (t "~/.config/ibus/rime/wubi86_jidian_user.dict.yaml"))) ; fallback to ibus location
(defun rime-wubi-dict-adder (word code)
  "Add a word and its code to the rime-wubi dictionary."
  (interactive "sWord: \nsCode: ")
  (with-temp-buffer
    (insert (format "%s\t%s\n" word code))
    (write-region (point-min) (point-max)  t)))

(defun rime-wubi-dict-adder-with-python (word)
  "Add a word and its code to the rime-wubi dictionary using Python."
  (interactive "sWord: ")
  (let ((command (format "python3 ~/.emacs.d/modules/rime-wubi-dict-adder/dictAdder.py %s -d %s" word rime-wubi-dict-adder-user-dict)))
    (shell-command command)))

(defun rime-wubi-dict-adder-from-selected-region ()
  "Add a word and its code to the rime-wubi dictionary using Python."
  (interactive)
  (let ((word (buffer-substring-no-properties (region-beginning) (region-end))))
    (rime-wubi-dict-adder-with-python word)))

(defun rime-wubi-dict-adder-2-character-back ()
  "Add the last two characters of a word to the rime-wubi dictionary using Python.
This function selects the two characters before the cursor, then calls
`rime-wubi-dict-adder-from-selected-region' to process them."
  (interactive)
  ;; Check if there are at least two characters before the cursor
  (if (< (point) 2)
      (message "Not enough characters before the cursor!")
    ;; Move the cursor back two characters
    (backward-char 2)
    ;; Set the mark at the current position (start of the region)
    (set-mark (point))
    ;; Move the cursor forward two characters (end of the region)
    (forward-char 2)
    ;; Call the function to process the selected region
    (rime-wubi-dict-adder-from-selected-region)
    ;; Deactivate the mark to cancel the selection
    (deactivate-mark)))

(provide 'rime-wubi-dict-adder)
;;; rime-wubi-dict-adder.el ends here
