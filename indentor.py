import sublime
import sublime_plugin

class IndentorCommand(sublime_plugin.TextCommand):

	'''
	View More of my work on https://github.com/omkarjc27 

	'''
	def run(self, edit):
		'''
		MIT License

		Copyright (c) 2019 Omkar Chalke

		Permission is hereby granted, free of charge, to any person obtaining a copy
		of this software and associated documentation files (the "Software"), to deal
		in the Software without restriction, including without limitation the rights
		to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
		copies of the Software, and to permit persons to whom the Software is
		furnished to do so, subject to the following conditions:

		The above copyright notice and this permission notice shall be included in all
		copies or substantial portions of the Software.

		THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
		IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
		FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
		AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
		LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
		OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
		SOFTWARE.

		'''

		file_region = sublime.Region(0,self.view.size())
		out_f = ''
		# Read the input file
		inl = self.view.lines(file_region)
		# Initial values for looping variables
		prev_line = ''
		prev_indention_value = 0
		extra_line = 0 	
		mul_comment = 0
		remain_semico = 0
		prev_comment = 0
		# Initiate Stack
		stack = self.Stack()
		stack.push(['',0])

		# Iterating over each line
		# Every iteration appends it's previous line to the file
		for ln in inl:
			line = self.view.substr(ln)
			# Handling line starting with # eg #define ... etc
			if line.strip().startswith("#") or line.strip().startswith("//"):
				prev_comment = 1
				if remain_semico == 1 :
					remain_semico = 0
					out_f+=prev_line+';\n'
				else:
					out_f+=prev_line+'\n'
				prev_line = line
			# Handling multiline comments
			elif line.strip().startswith("/*"):
				mul_comment = 1
				prev_comment = 1
				if remain_semico == 1 :
					remain_semico = 0
					out_f+=prev_line+';\n'
				else:
					out_f+=prev_line+'\n'
				prev_line = line
			elif line.strip().endswith("*/"):
				mul_comment = 0 
				prev_comment = 1
				if remain_semico == 1 :
					remain_semico = 0
					out_f+=prev_line+';\n'
				else:
					out_f+=prev_line+'\n'
				prev_line = line

			elif mul_comment == 1:
				prev_comment = 1
				if remain_semico == 1 :
					remain_semico = 0
					out_f+=prev_line+';\n'
				else:
					out_f+=prev_line+'\n'
				prev_line = line

			# Check if line is not blank
			elif len(line.strip()) > 0:
				indention_value = 0
				remain_semico = 0
				# Count indention
				while line[indention_value].isspace() or line[indention_value] == '\t':
					indention_value += 1
					if indention_value >= len(line):
						break
				# When going in inner scope
				remain_semico = 1
				if(indention_value > prev_indention_value):
					if(prev_line != None):
						out_f+=prev_line+'\n'
					item = stack.view_top()
					out_f += item[0]+'{\n'
					val = [line[slice(indention_value)],indention_value] 
					stack.push(val)
				# When coming to outer scope	
				elif(indention_value < prev_indention_value):
					if(prev_line != None):
						out_f += prev_line+';\n'
					while True:
						item = stack.view_top()
						if indention_value < item[1]:
							stack.pop()
							item = stack.view_top()
							out_f += item[0]+'}\n'
						else:
							break
				# Normal Line
				else:
					if(prev_line != None):
						if prev_comment != 1:
							out_f += prev_line+';\n'
						else:
							out_f += prev_line+'\n'

				prev_indention_value = indention_value
				prev_line = line
				if(extra_line == 1):
					out_f += '\n'
					extra_line = 0

			# When line is blank
			else:
				extra_line = 1

		# For Last line which is not added in the for loop 
		if(len(prev_line.strip())>0):
			# To add a buffer so that closing bracket is not immediately after the last statement
			#if(extra_line == 0):
			#	prev_line += '\n'
			if mul_comment == 1 or prev_comment == 1:
				prev_line += '\n'
			else:
				prev_line += ';\n'
			out_f += prev_line 
		
		# Pop stack untill empty so that all scopes that are not closed get closed 
		stack.pop()
		while stack.length() > 0:
			item = stack.pop()
			out_f += item[0]+'}\n'
		
		
		self.view.replace(edit,file_region,out_f[1:])


	class Stack:
		'''Class For Storing scopes and indention records'''
		def __init__(self):
			self.__storage = []
		def isEmpty(self):
			return len(self.__storage) == 0
		def push(self,element):
			self.__storage.append(element)
		def pop(self):
			return self.__storage.pop()
		def view_top(self):
			l = len(self.__storage)
			return self.__storage[l-1]
		def length(self):
			return len(self.__storage)