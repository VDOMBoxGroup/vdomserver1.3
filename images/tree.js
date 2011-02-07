/**************************************************************************
	Copyright (c) 2002-2005 Ordinatoria (ordinatoria@hotmail.fr)
	JavaScript Tree - www.ordinatoria.ifrance.fr
	Version 0.96	

	This script can be used freely as long as all copyright messages are
	intact.
**************************************************************************/

// Arrays for nodes and icons
var nodes			= new Array();;
var openNodes	= new Array();
var icons			= new Array(6);

// Loads all icons that are used in the tree
function preloadIcons() {
	icons[0] = new Image();
	icons[0].src = "../images/plus.gif";
	icons[1] = new Image();
	icons[1].src = "../images/plusbottom.gif";
	icons[2] = new Image();
	icons[2].src = "../images/minus.gif";
	icons[3] = new Image();
	icons[3].src = "../images/minusbottom.gif";
	icons[4] = new Image();
	icons[4].src = "../images/folder.gif";
	icons[5] = new Image();
	icons[5].src = "../images/folderopen.gif";
}

// Create the tree
function createTree(arrName, startNode, openNode) {
	nodes = arrName;
	if (nodes.length > 0) {
		preloadIcons();
		if (startNode == null) startNode = 0;
		if (openNode != 0 || openNode != null) setOpenNodes(openNode);
		CodeTree = "<table cellspacing=\"0\" cellpadding=\"0\">\n";
		if (startNode !=0) {
			var nodeValues = nodes[getArrayId(startNode)].split("|");
			CodeTree = CodeTree + "<tr>";
			CodeTree = CodeTree + "<td><img src=\"../images/folderopen.gif\" alt=\"Application\" /><a href=\"javascript: ocr(" + nodeValues[0] + ", '" + nodeValues[3] + "');\" onmouseover=\"window.status='" + nodeValues[2] + "';return true;\" onmouseout=\"window.status=' ';return true;\">" + nodeValues[2] + "</a></td>";
			CodeTree = CodeTree + "</tr>";
		}else{
			CodeTree = CodeTree + "<tr>";
			CodeTree = CodeTree + "<td><img src=\"../images/base.gif\" align=\"absbottom\" alt=\"\" />Website</td>";
			CodeTree = CodeTree + "</tr>";
		}
		CodeTree = CodeTree + "<tr id=\"divRights" + nodeValues[0] + "\" style=\"display: none;\">";
		CodeTree = CodeTree + "<td>";
		CodeTree = CodeTree + "<table cellspacing=\"0\" cellpadding=\"0\">";
		CodeTree = CodeTree + "<tr>";
		CodeTree = CodeTree + "<td background=\"../images/line.gif\" width=\"18\">&nbsp;</td>";
		CodeTree = CodeTree + "<td valign=\"top\"><table cellspacing=\"0\" cellpadding=\"0\">";
		CodeTree = CodeTree + "<tr><td><img src=\"../images/line.gif\" width=\"18\" /></td></tr>";
		CodeTree = CodeTree + "<tr><td valign=\"bottom\" height=\"18\"><img src=\"../images/joinbottom.gif\" alt=\"\" /></td></tr>";
		CodeTree = CodeTree + "</table></td>";
		CodeTree = CodeTree + "<td><iframe src name=\"FRights" + nodeValues[0] + "\" id=\"FRights" + nodeValues[0] + "\" height=\"50\" scrolling=\"no\" frameborder=\"0\" framespacing=\"0\" vspace=\"0\" hspace=\"0\"></iframe></td>";
		CodeTree = CodeTree + "</tr>";
		CodeTree = CodeTree + "</table>";
		CodeTree = CodeTree + "</td>";
		CodeTree = CodeTree + "</tr>";	

		var recursedNodes = new Array();
		addNode(startNode, recursedNodes);
		CodeTree = CodeTree + "</table>";
		document.write(CodeTree);
	}
}

// Returns the position of a node in the array
function getArrayId(node) {
	for (i=0; i<nodes.length; i++) {
		var nodeValues = nodes[i].split("|");
		if (nodeValues[0]==node) return i;
	}
}

// Puts in array nodes that will be open
function setOpenNodes(openNode) {
	for (i=0; i<nodes.length; i++) {
		var nodeValues = nodes[i].split("|");
		if (nodeValues[0]==openNode) {
			openNodes.push(nodeValues[0]);
			setOpenNodes(nodeValues[1]);
		}
	} 
}

// Checks if a node is open
function isNodeOpen(node) {
	for (i=0; i<openNodes.length; i++)
		if (openNodes[i]==node) return true;
	return false;
}
// Checks if a node has any children
function hasChildNode(parentNode) {
	for (i=0; i< nodes.length; i++) {
		var nodeValues = nodes[i].split("|");
		if (nodeValues[1] == parentNode) return true;
	}
	return false;
}
// Checks if a node is the last sibling
function lastSibling (node, parentNode) {
	var lastChild = 0;
	for (i=0; i< nodes.length; i++) {
		var nodeValues = nodes[i].split("|");
		if (nodeValues[1] == parentNode)
			lastChild = nodeValues[0];
	}
	if (lastChild==node) return true;
	return false;
}
// Adds a new node to the tree
function addNode(parentNode, recursedNodes) {
	for (var i = 0; i < nodes.length; i++) {

		var nodeValues = nodes[i].split("|");
		if (nodeValues[1] == parentNode) {
			
			var ls	= lastSibling(nodeValues[0], nodeValues[1]);
			var hcn	= hasChildNode(nodeValues[0]);
			var ino = isNodeOpen(nodeValues[0]);
			
			CodeTree = CodeTree + "<tr>";
			CodeTree = CodeTree + "<td>";
			CodeTree = CodeTree + "<table cellspacing=\"0\" cellpadding=\"0\">";
			CodeTree = CodeTree + "<tr>";

			// Write out line & empty icons
			for (g=0; g<recursedNodes.length; g++) {
				if (recursedNodes[g] == 1) CodeTree = CodeTree + "<td><img src=\"../images/line.gif\" alt=\"\" /></td>";
				else  CodeTree = CodeTree + "<td><img src=\"../images/empty.gif\" alt=\"\" /></td>";
			}

			// put in array line & empty icons
			if (ls) recursedNodes.push(0);
			else recursedNodes.push(1);

			// Write out join icons
			if (hcn) {
				if (ls) {
					CodeTree = CodeTree + "<td><a href=\"javascript: oc(" + nodeValues[0] + ", 1);\"><img id=\"join" + nodeValues[0] + "\" src=\"../images/";
					 	if (ino) CodeTree = CodeTree + "minus";
						else CodeTree = CodeTree + "plus";
					CodeTree = CodeTree + "bottom.gif\" alt=\"Open/Close node\" /></a></td>";
				} else {
					CodeTree = CodeTree + "<td><a href=\"javascript: oc(" + nodeValues[0] + ", 0);\"><img id=\"join" + nodeValues[0] + "\" src=\"../images/";
						if (ino) CodeTree = CodeTree + "minus";
						else CodeTree = CodeTree + "plus";
					CodeTree = CodeTree + ".gif\" alt=\"Open/Close node\" /></a></td>";
				}
			} else {
				if (ls) CodeTree = CodeTree + "<td><img src=\"../images/joinbottom.gif\" alt=\"\" /></td>";
				else CodeTree = CodeTree + "<td><img src=\"../images/join.gif\" alt=\"\" /></td>";
			}

			// Write out folder & page icons
			if (hcn) {
				CodeTree = CodeTree + "<td><img id=\"icon" + nodeValues[0] + "\" src=\"../images/folder";
					if (ino) CodeTree = CodeTree + "open";
				CodeTree = CodeTree + ".gif\" alt=\"Container\" /></td>";
			} else CodeTree = CodeTree + "<td><img id=\"icon" + nodeValues[0] + "\" src=\"../images/page.gif\" alt=\"Object\" /></td>";
			
			CodeTree = CodeTree + "<td><a href=\"javascript: ocr(" + nodeValues[0] + ", '" + nodeValues[3] + "');\" onmouseover=\"window.status='" + nodeValues[2] + "';return true;\" onmouseout=\"window.status=' ';return true;\">";
			
			// Write out node name
			CodeTree = CodeTree + nodeValues[2];

			CodeTree = CodeTree + "</a></td>";
			CodeTree = CodeTree + "</tr>";
			CodeTree = CodeTree + "</table>";
			CodeTree = CodeTree + "</td>";
			CodeTree = CodeTree + "</tr>";			
			
			CodeTree = CodeTree + "<tr id=\"divRights" + nodeValues[0] + "\" style=\"display: none;\">";
			CodeTree = CodeTree + "<td>";
			CodeTree = CodeTree + "<table cellspacing=\"0\" cellpadding=\"0\">";
			CodeTree = CodeTree + "<tr>";
			for (g=0; g<recursedNodes.length; g++) {
				if (recursedNodes[g] == 1){
					CodeTree = CodeTree + "<td background=\"../images/line.gif\" width=\"18\">&nbsp;</td>";
				}else{
					CodeTree = CodeTree + "<td><img src=\"../images/empty.gif\" alt=\"\" /></td>";
				}
			};
			if (hcn){
				CodeTree = CodeTree + "<td id=\"LC" + nodeValues[0] + "\"><img src=\"../images/empty.gif\" alt=\"\" /></td>\n";
			};
			CodeTree = CodeTree + "<td valign=\"top\"><table cellspacing=\"0\" cellpadding=\"0\">";
			CodeTree = CodeTree + "<tr><td><img src=\"../images/line.gif\" width=\"18\" /></td></tr>";
			CodeTree = CodeTree + "<tr><td valign=\"bottom\" height=\"18\"><img src=\"../images/joinbottom.gif\" alt=\"\" /></td></tr>";
			CodeTree = CodeTree + "</table></td>";
			CodeTree = CodeTree + "<td><iframe src name=\"FRights" + nodeValues[0] + "\" id=\"FRights" + nodeValues[0] + "\" height=\"50\" scrolling=\"no\" frameborder=\"no\" framespacing=\"0\" vspace=\"0\" hspace=\"0\"></iframe></td>";
			CodeTree = CodeTree + "</tr>";
			CodeTree = CodeTree + "</table>";
			CodeTree = CodeTree + "</td>";
			CodeTree = CodeTree + "</tr>";
			
			// If node has children write out divs and go deeper
			if (hcn) {
				CodeTree = CodeTree + "<tr>";
				CodeTree = CodeTree + "<td>";
				CodeTree = CodeTree + "<table cellspacing=\"0\" cellpadding=\"0\" id=\"div" + nodeValues[0] + "\"";
					if (!ino) CodeTree = CodeTree + " style=\"display: none;\"";
				CodeTree = CodeTree + ">";
				addNode(nodeValues[0], recursedNodes);
				CodeTree = CodeTree + "</table>";
				CodeTree = CodeTree + "</td>";
				CodeTree = CodeTree + "</tr>";
			}			
				

			// remove last line or empty icon 
			recursedNodes.pop();
		}
	}
}

// Opens or closes a node
function oc(node, bottom) {
	var theDiv = document.getElementById("div" + node);
	var theJoin	= document.getElementById("join" + node);
	var theIcon = document.getElementById("icon" + node);
	var LineCache = document.getElementById("LC" + node);

	if (theDiv.style.display == 'none') {
		if (bottom==1) theJoin.src = icons[3].src;
		else theJoin.src = icons[2].src;
		theIcon.src = icons[5].src;
		theDiv.style.display = '';
		LineCache.background='../images/line.gif';
	} else {
		if (bottom==1) theJoin.src = icons[1].src;
		else theJoin.src = icons[0].src;
		theIcon.src = icons[4].src;
		theDiv.style.display = 'none';
		LineCache.background='';
	}
}

// Opens or closes rights
function ocr(node,linkR) {
	var theDiv = document.getElementById("divRights" + node);
	var theIcon = document.getElementById("icon" + node);
	
	if (theDiv.style.display == 'none') {
		theDiv.style.display = '';
		eval('FRights' + node + '.location=\'' + linkR + '&NbTree=' + node + '\';');
	} else {
		theDiv.style.display = 'none';
	}
}

// Push and pop not implemented in IE
if(!Array.prototype.push) {
	function array_push() {
		for(var i=0;i<arguments.length;i++)
			this[this.length]=arguments[i];
		return this.length;
	}
	Array.prototype.push = array_push;
}
if(!Array.prototype.pop) {
	function array_pop(){
		lastElement = this[this.length-1];
		this.length = Math.max(this.length-1,0);
		return lastElement;
	}
	Array.prototype.pop = array_pop;
}
